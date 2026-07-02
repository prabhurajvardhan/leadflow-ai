from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from app.core.logger import get_logger

logger = get_logger("ai_provider_base")


@dataclass
class AIResponse:
    """Response from an AI provider."""
    content: str
    model: str
    provider: str
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    raw_response: Optional[Dict[str, Any]] = None


@dataclass
class Message:
    """A chat message."""
    role: str  # "system", "user", "assistant"
    content: str


class BaseAIProvider(ABC):
    """Base class for AI providers.
    
    This interface allows swapping AI providers (OpenAI, Anthropic, 
    OpenRouter, local models) without changing the rest of the application.
    """
    
    name: str = "base"
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = get_logger(f"ai_{self.name}")
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> AIResponse:
        """Generate a response from a prompt."""
        pass
    
    @abstractmethod
    async def chat(self, messages: List[Message], **kwargs) -> AIResponse:
        """Generate a response from a chat conversation."""
        pass
    
    async def validate(self) -> bool:
        """Validate provider configuration."""
        return True
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} provider>"
