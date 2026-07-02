from typing import Dict, Any, Optional
import httpx
from app.outreach.providers.base import BaseEmailProvider, EmailResult
from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger("resend_provider")


class ResendEmailProvider(BaseEmailProvider):
    """Resend email provider.
    
    Sends transactional emails using the Resend API.
    https://resend.com
    """
    
    name = "resend"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.api_key = self.config.get("api_key") or settings.RESEND_API_KEY
        self.base_url = "https://api.resend.com"
        self.timeout = self.config.get("timeout", 30)
    
    async def validate(self) -> bool:
        """Validate Resend configuration."""
        if not self.api_key:
            self.logger.error("Resend API key not configured")
            return False
        return True
    
    async def send(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_email: str = None,
        from_name: str = None,
        reply_to: str = None,
        attachments: list = None,
        **kwargs
    ) -> EmailResult:
        """Send an email via Resend API.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (HTML or plain text)
            from_email: Sender email (optional, uses default)
            from_name: Sender name (optional)
            reply_to: Reply-to address (optional)
            attachments: List of attachments (optional)
            
        Returns:
            EmailResult with success status and message ID
        """
        if not await self.validate():
            return EmailResult(success=False, error="Resend API key not configured")
        
        try:
            sender_email = from_email or self.config.get("from_email") or settings.SMTP_FROM_EMAIL
            sender_name = from_name or self.config.get("from_name") or settings.SMTP_FROM_NAME
            
            # Format from address
            from_address = f"{sender_name} <{sender_email}>"
            
            # Build email payload
            payload: Dict[str, Any] = {
                "from": from_address,
                "to": [to_email],
                "subject": subject,
            }
            
            # Determine if HTML or plain text
            if "<html" in body.lower() or "<body" in body.lower():
                payload["html"] = body
            else:
                payload["text"] = body
            
            if reply_to:
                payload["reply_to"] = reply_to
            
            # Add attachments if provided
            if attachments:
                payload["attachments"] = [
                    {
                        "filename": att.get("filename", "attachment"),
                        "content": att.get("content", ""),
                        "type": att.get("type", "application/octet-stream")
                    }
                    for att in attachments
                ]
            
            self.logger.info(f"Sending email to {to_email} via Resend: {subject}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/emails",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                )
                
                if response.status_code == 201:
                    data = response.json()
                    message_id = data.get("id")
                    self.logger.info(f"Email sent successfully to {to_email}, message_id: {message_id}")
                    return EmailResult(
                        success=True,
                        message_id=message_id,
                        raw_response=data
                    )
                else:
                    error_msg = response.text
                    self.logger.error(f"Resend API error: {response.status_code} - {error_msg}")
                    return EmailResult(
                        success=False,
                        error=f"API error {response.status_code}: {error_msg}",
                        raw_response=response.json() if response.headers.get("content-type", "").startswith("application/json") else None
                    )
                    
        except httpx.TimeoutException:
            self.logger.error(f"Resend request timeout after {self.timeout}s")
            return EmailResult(success=False, error="Request timeout")
        except Exception as e:
            self.logger.error(f"Unexpected error sending to {to_email}: {e}")
            return EmailResult(success=False, error=str(e))
    
    async def send_batch(
        self,
        emails: list,
        from_email: str = None,
        from_name: str = None
    ) -> list:
        """Send multiple emails in batch.
        
        Args:
            emails: List of dicts with to, subject, body keys
            from_email: Sender email
            from_name: Sender name
            
        Returns:
            List of EmailResult objects
        """
        results = []
        
        sender_email = from_email or self.config.get("from_email") or settings.SMTP_FROM_EMAIL
        sender_name = from_name or self.config.get("from_name") or settings.SMTP_FROM_NAME
        from_address = f"{sender_name} <{sender_email}>"
        
        for email_data in emails:
            result = await self.send(
                to_email=email_data["to"],
                subject=email_data["subject"],
                body=email_data["body"],
                from_email=from_address
            )
            results.append(result)
            
            # Rate limiting - be nice to Resend's API
            import asyncio
            await asyncio.sleep(0.1)
        
        return results
