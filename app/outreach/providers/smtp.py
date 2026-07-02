from typing import Dict, Any, Optional
import asyncio
import email.mime.text
import email.mime.multipart
from email.header import Header
import aiosmtplib
from app.outreach.providers.base import BaseEmailProvider, EmailResult
from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger("smtp_provider")


class SMTPEmailProvider(BaseEmailProvider):
    """SMTP email provider.
    
    Sends emails using SMTP protocol. Supports Gmail, Office 365,
    and any standard SMTP server.
    """
    
    name = "smtp"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.host = self.config.get("host") or settings.SMTP_HOST
        self.port = self.config.get("port") or settings.SMTP_PORT
        self.username = self.config.get("username") or settings.SMTP_USER
        self.password = self.config.get("password") or settings.SMTP_PASSWORD
        self.use_tls = self.config.get("use_tls") if "use_tls" in self.config else settings.SMTP_USE_TLS
        self.from_email = self.config.get("from_email") or settings.SMTP_FROM_EMAIL
        self.from_name = self.config.get("from_name") or settings.SMTP_FROM_NAME
        self.timeout = self.config.get("timeout", 30)
    
    async def validate(self) -> bool:
        """Validate SMTP configuration."""
        if not self.host:
            self.logger.error("SMTP host not configured")
            return False
        if not self.username or not self.password:
            self.logger.warning("SMTP credentials not configured")
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
        """Send an email via SMTP.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (plain text or HTML)
            from_email: Sender email (optional, uses default)
            from_name: Sender name (optional)
            reply_to: Reply-to address (optional)
            attachments: List of attachments (optional)
            
        Returns:
            EmailResult with success status and message ID
        """
        try:
            # Prepare message
            msg = email.mime.multipart.MIMEMultipart("alternative")
            
            # Set headers
            sender_email = from_email or self.from_email or self.username
            sender_name = from_name or self.from_name or ""
            
            msg["From"] = self._format_address(sender_email, sender_name)
            msg["To"] = to_email
            msg["Subject"] = Header(subject, "utf-8")
            
            if reply_to:
                msg["Reply-To"] = reply_to
            
            # Add body
            if "<html" in body.lower() or "<body" in body.lower():
                msg.attach(email.mime.text.MIMEText(body, "html", "utf-8"))
            else:
                msg.attach(email.mime.text.MIMEText(body, "plain", "utf-8"))
            
            # Send email
            self.logger.info(f"Sending email to {to_email}: {subject}")
            
            if self.use_tls:
                await aiosmtplib.send(
                    msg,
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    use_tls=True,
                    timeout=self.timeout
                )
            else:
                await aiosmtplib.send(
                    msg,
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    start_tls=True,
                    timeout=self.timeout
                )
            
            message_id = msg["Message-ID"]
            self.logger.info(f"Email sent successfully to {to_email}, message_id: {message_id}")
            
            return EmailResult(
                success=True,
                message_id=message_id,
                raw_response={"status": "sent"}
            )
            
        except aiosmtplib.SMTPException as e:
            self.logger.error(f"SMTP error sending to {to_email}: {e}")
            return EmailResult(
                success=False,
                error=str(e)
            )
        except Exception as e:
            self.logger.error(f"Unexpected error sending to {to_email}: {e}")
            return EmailResult(
                success=False,
                error=str(e)
            )
    
    def _format_address(self, email: str, name: str = None) -> str:
        """Format email address with optional name."""
        if name:
            return f"{Header(name, 'utf-8')} <{email}>"
        return email
