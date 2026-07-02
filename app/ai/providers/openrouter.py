from typing import List, Dict, Any, Optional
import json
import httpx
from app.ai.providers.base import BaseAIProvider, AIResponse, Message
from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger("openrouter_provider")


class OpenRouterProvider(BaseAIProvider):
    """OpenRouter AI provider.
    
    OpenRouter provides access to multiple AI models through a unified API.
    """
    
    name = "openrouter"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.api_key = self.config.get("api_key") or settings.OPENROUTER_API_KEY
        self.base_url = self.config.get("base_url") or settings.OPENROUTER_BASE_URL
        self.default_model = self.config.get("model") or settings.OPENROUTER_DEFAULT_MODEL
        self.timeout = self.config.get("timeout", 60)
    
    async def validate(self) -> bool:
        """Validate provider configuration."""
        if not self.api_key:
            self.logger.error("OpenRouter API key not configured")
            return False
        return True
    
    async def generate(self, prompt: str, model: str = None, 
                     temperature: float = 0.7, **kwargs) -> AIResponse:
        """Generate a response from a prompt."""
        model = model or self.default_model
        
        messages = [Message(role="user", content=prompt)]
        return await self.chat(messages, model=model, temperature=temperature, **kwargs)
    
    async def chat(self, messages: List[Message], model: str = None,
                  temperature: float = 0.7, max_tokens: int = 4096,
                  **kwargs) -> AIResponse:
        """Generate a response from a chat conversation."""
        model = model or self.default_model
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://leadflow.ai",
            "X-Title": "LeadFlow AI"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code != 200:
                    self.logger.error(f"OpenRouter error: {response.status_code} - {response.text}")
                    raise Exception(f"OpenRouter API error: {response.status_code}")
                
                data = response.json()
                
                return AIResponse(
                    content=data["choices"][0]["message"]["content"],
                    model=model,
                    provider=self.name,
                    tokens_used=data.get("usage", {}).get("total_tokens"),
                    raw_response=data
                )
                
        except httpx.TimeoutException:
            self.logger.error(f"OpenRouter timeout after {self.timeout}s")
            raise Exception("OpenRouter request timeout")
        except Exception as e:
            self.logger.error(f"OpenRouter error: {e}")
            raise
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=headers
                )
                
                if response.status_code == 200:
                    return response.json().get("data", [])
                return []
        except Exception as e:
            self.logger.error(f"Failed to list models: {e}")
            return []
