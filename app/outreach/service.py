from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.outreach.providers.base import BaseEmailProvider, EmailResult
from app.outreach.providers.smtp import SMTPEmailProvider
from app.outreach.providers.resend import ResendEmailProvider
from app.database.models import SentEmail, EmailStatus, Campaign
from app.database.repository.lead_repository import LeadRepository
from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger("outreach_service")


def get_email_provider() -> BaseEmailProvider:
    """Get the configured email provider based on settings."""
    provider_type = getattr(settings, 'EMAIL_PROVIDER', 'smtp')
    
    if provider_type == 'resend':
        return ResendEmailProvider()
    else:
        return SMTPEmailProvider()


class OutreachService:
    """Service for managing email outreach campaigns."""
    
    def __init__(
        self,
        session: AsyncSession,
        email_provider: BaseEmailProvider = None
    ):
        self.session = session
        self.email_provider = email_provider or get_email_provider()
        self.lead_repo = LeadRepository(session)
        self.logger = logger
        self.daily_limit = settings.EMAIL_DAILY_LIMIT
    
    async def send_email(
        self,
        lead_id: int,
        contact_id: int,
        campaign_id: int,
        subject: str,
        body: str,
        to_email: str,
        scheduled_at: datetime = None
    ) -> SentEmail:
        """Send an email to a lead.
        
        Args:
            lead_id: ID of the lead
            contact_id: ID of the contact
            campaign_id: ID of the campaign
            subject: Email subject
            body: Email body
            to_email: Recipient email address
            scheduled_at: Optional scheduled send time
            
        Returns:
            SentEmail object
        """
        self.logger.info(f"Sending email to lead {lead_id}, contact {contact_id}")
        
        # Create tracking ID
        tracking_id = str(uuid.uuid4())[:8]
        
        # Create sent email record
        sent_email = SentEmail(
            campaign_id=campaign_id,
            lead_id=lead_id,
            contact_id=contact_id,
            to_email=to_email,
            subject=subject,
            body=body,
            status=EmailStatus.PENDING.value,
            tracking_id=tracking_id
        )
        
        self.session.add(sent_email)
        await self.session.flush()
        await self.session.refresh(sent_email)
        
        # Send if not scheduled
        if not scheduled_at or scheduled_at <= datetime.utcnow():
            await self._send_now(sent_email)
        else:
            sent_email.status = EmailStatus.PENDING.value
            self.logger.info(f"Email scheduled for {scheduled_at}")
        
        return sent_email
    
    async def _send_now(self, sent_email: SentEmail) -> EmailResult:
        """Send email immediately via provider."""
        try:
            result = await self.email_provider.send(
                to_email=sent_email.to_email,
                subject=sent_email.subject,
                body=sent_email.body
            )
            
            if result.success:
                sent_email.status = EmailStatus.SENT.value
                sent_email.sent_at = datetime.utcnow()
                sent_email.message_id = result.message_id
                self.logger.info(f"Email sent successfully: {sent_email.tracking_id}")
            else:
                sent_email.status = EmailStatus.FAILED.value
                sent_email.error_message = result.error
                self.logger.error(f"Email failed: {result.error}")
            
            sent_email.smtp_response = result.raw_response or {}
            await self.session.flush()
            
            return result
            
        except Exception as e:
            sent_email.status = EmailStatus.FAILED.value
            sent_email.error_message = str(e)
            await self.session.flush()
            self.logger.error(f"Email send error: {e}")
            return EmailResult(success=False, error=str(e))
    
    async def send_campaign_emails(
        self,
        campaign_id: int,
        lead_ids: List[int]
    ) -> Dict[str, int]:
        """Send emails to multiple leads for a campaign.
        
        Args:
            campaign_id: ID of the campaign
            lead_ids: List of lead IDs to email
            
        Returns:
            Dictionary with counts of sent/failed emails
        """
        self.logger.info(f"Sending campaign {campaign_id} to {len(lead_ids)} leads")
        
        sent_count = 0
        failed_count = 0
        
        for lead_id in lead_ids:
            try:
                lead = await self.lead_repo.get_by_id(lead_id)
                if not lead:
                    self.logger.warning(f"Lead {lead_id} not found, skipping")
                    failed_count += 1
                    continue
                
                # Get primary contact
                contact = next(
                    (c for c in lead.contacts if c.is_primary),
                    lead.contacts[0] if lead.contacts else None
                )
                
                if not contact or not contact.email:
                    self.logger.warning(f"No valid contact for lead {lead_id}, skipping")
                    failed_count += 1
                    continue
                
                # Get campaign data
                from sqlalchemy import select
                from app.database.models import Campaign
                
                result = await self.session.execute(
                    select(Campaign).where(Campaign.id == campaign_id)
                )
                campaign = result.scalar_one_or_none()
                
                if not campaign:
                    self.logger.error(f"Campaign {campaign_id} not found")
                    failed_count += 1
                    continue
                
                await self.send_email(
                    lead_id=lead_id,
                    contact_id=contact.id,
                    campaign_id=campaign_id,
                    subject=campaign.subject or "Quick question",
                    body=campaign.email_body or "",
                    to_email=contact.email
                )
                
                sent_count += 1
                
                # Rate limiting
                import asyncio
                await asyncio.sleep(1)  # 1 email per second
                
            except Exception as e:
                self.logger.error(f"Failed to send to lead {lead_id}: {e}")
                failed_count += 1
        
        # Update campaign stats
        from sqlalchemy import update
        await self.session.execute(
            update(Campaign).where(Campaign.id == campaign_id).values(
                sent_count=Campaign.sent_count + sent_count,
                status="running"
            )
        )
        await self.session.commit()
        
        return {"sent": sent_count, "failed": failed_count}
    
    async def track_email_status(
        self,
        tracking_id: str,
        status: str,
        event_data: Dict[str, Any] = None
    ) -> Optional[SentEmail]:
        """Track email status updates.
        
        Args:
            tracking_id: Unique tracking ID
            status: New status
            event_data: Additional event data
            
        Returns:
            Updated SentEmail or None
        """
        from sqlalchemy import select, update
        
        result = await self.session.execute(
            select(SentEmail).where(SentEmail.tracking_id == tracking_id)
        )
        sent_email = result.scalar_one_or_none()
        
        if not sent_email:
            self.logger.warning(f"Email with tracking_id {tracking_id} not found")
            return None
        
        # Update status based on event
        now = datetime.utcnow()
        updates = {}
        
        if status == "delivered":
            updates["status"] = EmailStatus.DELIVERED.value
            updates["delivered_at"] = now
        elif status == "opened":
            updates["status"] = EmailStatus.OPENED.value
            updates["opened_at"] = now
        elif status == "replied":
            updates["status"] = EmailStatus.REPLIED.value
            updates["replied_at"] = now
        elif status == "bounced":
            updates["status"] = EmailStatus.BOUNCED.value
            updates["bounced_at"] = now
        
        if updates:
            await self.session.execute(
                update(SentEmail)
                .where(SentEmail.id == sent_email.id)
                .values(**updates)
            )
            await self.session.commit()
            
            self.logger.info(f"Email {tracking_id} status updated to {status}")
        
        return sent_email
    
    async def get_campaign_stats(self, campaign_id: int) -> Dict[str, int]:
        """Get statistics for a campaign."""
        from sqlalchemy import select, func
        from app.database.models import SentEmail
        
        # Get status counts
        result = await self.session.execute(
            select(
                SentEmail.status,
                func.count(SentEmail.id)
            ).where(
                SentEmail.campaign_id == campaign_id
            ).group_by(SentEmail.status)
        )
        
        stats = {
            "total": 0,
            "pending": 0,
            "sent": 0,
            "delivered": 0,
            "opened": 0,
            "replied": 0,
            "bounced": 0,
            "failed": 0
        }
        
        for status, count in result:
            stats[status] = count
            stats["total"] += count
        
        return stats
