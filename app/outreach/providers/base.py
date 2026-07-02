from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from app.core.logger import get_logger

logger = get_logger("email_provider_base")


@dataclass
class EmailResult:
    """Result of sending an email."""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


class BaseEmailProvider(ABC):
    """Base class for email providers.
    
    This interface allows swapping email providers (SMTP, Gmail, Resend,
    SendGrid, SES) without changing the rest of the application.
    """
    
    name: str = "base"
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = get_logger(f"email_{self.name}")
    
    @abstractmethod
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
        """Send an email."""
        pass
    
    async def validate(self) -> bool:
        """Validate provider configuration."""
        return True
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} email provider>"
