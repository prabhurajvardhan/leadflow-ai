from typing import Dict, Any, List, Optional
import boto3
import json
from app.ai.providers.base import BaseAIProvider, AIResponse, Message
from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger("bedrock_provider")


class BedrockAIProvider(BaseAIProvider):
    """Amazon Bedrock AI provider.
    
    Uses AWS Bedrock to access AI models including Amazon Nova.
    Requires AWS credentials with Bedrock access.
    """
    
    name = "bedrock"
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.model_id = self.config.get("model_id") or settings.BEDROCK_MODEL_ID
        self.region = self.config.get("region") or settings.AWS_REGION
        
        # Initialize boto3 client
        self.client = self._get_client()
    
    def _get_client(self):
        """Get AWS Bedrock client."""
        try:
            client_kwargs = {
                "region_name": self.region,
            }
            
            # Use provided credentials or default credential chain
            access_key = self.config.get("aws_access_key_id") or settings.AWS_ACCESS_KEY_ID
            secret_key = self.config.get("aws_secret_access_key") or settings.AWS_SECRET_ACCESS_KEY
            
            if access_key and secret_key:
                client_kwargs["aws_access_key_id"] = access_key
                client_kwargs["aws_secret_access_key"] = secret_key
            
            return boto3.client("bedrock-runtime", **client_kwargs)
        except Exception as e:
            self.logger.error(f"Failed to initialize Bedrock client: {e}")
            return None
    
    async def validate(self) -> bool:
        """Validate Bedrock configuration."""
        if not self.client:
            self.logger.error("Bedrock client not initialized")
            return False
        
        # Test with a simple inference call
        try:
            # Try to invoke the model
            body = {
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": "Hi"}]
                    }
                ],
                "inferenceConfig": {
                    "maxTokens": 10,
                    "topP": 0.9,
                    "temperature": 0.7
                }
            }
            
            response = self.client.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(body)
            )
            
            return response["ResponseMetadata"]["HTTPStatusCode"] == 200
        except Exception as e:
            self.logger.error(f"Bedrock validation failed: {e}")
            return False
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        **kwargs
    ) -> AIResponse:
        """Generate text from a prompt.
        
        Args:
            prompt: The prompt text
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            AIResponse with generated text
        """
        try:
            self.logger.info(f"Generating with Bedrock model: {self.model_id}")
            
            # Format for Nova models
            body = {
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ],
                "inferenceConfig": {
                    "maxTokens": max_tokens,
                    "topP": kwargs.get("top_p", 0.9),
                    "temperature": temperature
                }
            }
            
            response = self.client.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(body)
            )
            
            response_body = json.loads(response["body"].read())
            
            # Extract response based on Nova format
            if "output" in response_body and "message" in response_body["output"]:
                content = response_body["output"]["message"]["content"]
                if isinstance(content, list) and len(content) > 0:
                    text = content[0].get("text", "")
                else:
                    text = str(content)
            elif "completion" in response_body:
                text = response_body["completion"]
            else:
                text = str(response_body)
            
            return AIResponse(
                content=text,
                raw_response=response_body
            )
            
        except Exception as e:
            self.logger.error(f"Bedrock generation error: {e}")
            return AIResponse(content="", error=str(e))
    
    async def chat(
        self,
        messages: List[Message],
        max_tokens: int = 2048,
        temperature: float = 0.7,
        **kwargs
    ) -> AIResponse:
        """Chat with the model using conversation history.
        
        Args:
            messages: List of conversation messages
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            AIResponse with model's reply
        """
        try:
            self.logger.info(f"Chatting with Bedrock model: {self.model_id}")
            
            # Convert messages to Nova format
            nova_messages = []
            for msg in messages:
                content = msg.content
                if isinstance(content, list):
                    # Handle mixed content
                    text_parts = [c.get("text", "") if isinstance(c, dict) else str(c) for c in content]
                    content = "\n".join(filter(None, text_parts))
                
                nova_messages.append({
                    "role": msg.role,
                    "content": [{"text": str(content)}]
                })
            
            body = {
                "messages": nova_messages,
                "inferenceConfig": {
                    "maxTokens": max_tokens,
                    "topP": kwargs.get("top_p", 0.9),
                    "temperature": temperature
                }
            }
            
            response = self.client.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(body)
            )
            
            response_body = json.loads(response["body"].read())
            
            # Extract response
            if "output" in response_body and "message" in response_body["output"]:
                content = response_body["output"]["message"]["content"]
                if isinstance(content, list) and len(content) > 0:
                    text = content[0].get("text", "")
                else:
                    text = str(content)
            elif "completion" in response_body:
                text = response_body["completion"]
            else:
                text = str(response_body)
            
            return AIResponse(
                content=text,
                raw_response=response_body
            )
            
        except Exception as e:
            self.logger.error(f"Bedrock chat error: {e}")
            return AIResponse(content="", error=str(e))
    
    async def analyze_lead(
        self,
        company_name: str,
        domain: str,
        description: str = None,
        technologies: List[str] = None
    ) -> Dict[str, Any]:
        """Analyze a lead using Bedrock/Nova.
        
        Args:
            company_name: Name of the company
            domain: Company website domain
            description: Company description
            technologies: List of detected technologies
            
        Returns:
            Analysis results dict
        """
        from app.ai.templates.prompts import get_lead_analysis_prompt
        
        prompt = get_lead_analysis_prompt(
            company_name=company_name,
            domain=domain,
            description=description,
            technologies=technologies or []
        )
        
        response = await self.chat(
            messages=[Message(role="user", content=prompt)],
            max_tokens=2048,
            temperature=0.3
        )
        
        if response.error:
            return {"error": response.error}
        
        # Try to parse JSON from response
        try:
            # Look for JSON in the response
            content = response.content
            
            # Handle markdown code blocks
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                content = content[start:end].strip()
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                content = content[start:end].strip()
            
            return json.loads(content)
        except json.JSONDecodeError:
            self.logger.warning("Could not parse JSON from analysis response")
            return {"summary": response.content}
    
    async def generate_outreach_email(
        self,
        company_name: str,
        contact_name: str,
        contact_title: str = None,
        personalization_hints: Dict[str, Any] = None
    ) -> Dict[str, str]:
        """Generate a personalized outreach email.
        
        Args:
            company_name: Target company name
            contact_name: Contact person's name
            contact_title: Contact's job title
            personalization_hints: Additional hints for personalization
            
        Returns:
            Dict with 'subject' and 'body'
        """
        from app.ai.templates.prompts import get_outreach_email_prompt
        
        prompt = get_outreach_email_prompt(
            company_name=company_name,
            contact_name=contact_name,
            contact_title=contact_title,
            personalization_hints=personalization_hints or {}
        )
        
        response = await self.chat(
            messages=[Message(role="user", content=prompt)],
            max_tokens=2048,
            temperature=0.7
        )
        
        if response.error:
            return {"subject": "", "body": "", "error": response.error}
        
        # Try to parse JSON from response
        try:
            content = response.content
            
            # Handle markdown code blocks
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                content = content[start:end].strip()
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                content = content[start:end].strip()
            
            return json.loads(content)
        except json.JSONDecodeError:
            self.logger.warning("Could not parse JSON from email generation response")
            return {"subject": "Quick question", "body": response.content}
