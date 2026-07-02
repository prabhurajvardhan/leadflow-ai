from typing import Dict, Any, Optional, List
import json
from app.ai.providers.base import BaseAIProvider, AIResponse, Message
from app.ai.providers.openrouter import OpenRouterProvider
from app.ai.providers.bedrock import BedrockAIProvider
from app.ai.templates.prompts import (
    ANALYSIS_SYSTEM_PROMPT,
    analysis_prompt,
    email_generation_prompt,
    scoring_prompt,
    reply_analysis_prompt,
    opportunity_prompt
)
from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger("ai_analyzer")


def get_ai_provider() -> BaseAIProvider:
    """Get the configured AI provider."""
    provider_type = settings.DEFAULT_AI_PROVIDER.lower()
    
    if provider_type == "bedrock":
        return BedrockAIProvider()
    elif provider_type == "openrouter":
        return OpenRouterProvider()
    return BedrockAIProvider()  # Default: Bedrock with Nova Micro


class AIAnalyzer:
    """AI-powered lead analyzer.
    
    Uses configurable AI providers to analyze leads, generate emails,
    and score opportunities.
    """
    
    def __init__(self, provider: BaseAIProvider = None):
        self.provider = provider or get_ai_provider()
        self.logger = logger
    
    async def analyze_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a lead and generate insights.
        
        Args:
            lead_data: Dictionary containing lead information
            
        Returns:
            Dictionary with analysis results
        """
        self.logger.info(f"Analyzing lead: {lead_data.get('company_name', 'Unknown')}")
        
        try:
            # Generate analysis
            response = await self.provider.generate(
                prompt=analysis_prompt(lead_data),
                system_prompt=ANALYSIS_SYSTEM_PROMPT
            )
            
            # Parse JSON response
            analysis = self._parse_json_response(response.content)
            
            # Add metadata
            analysis["ai_provider"] = response.provider
            analysis["ai_model"] = response.model
            analysis["tokens_used"] = response.tokens_used
            
            # Generate score
            score_result = await self.score_lead(lead_data)
            analysis.update(score_result)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Lead analysis failed: {e}")
            return {
                "error": str(e),
                "summary": "Analysis failed",
                "pain_points": [],
                "opportunities": [],
                "recommendations": []
            }
    
    async def score_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Score a lead based on various factors.
        
        Args:
            lead_data: Dictionary containing lead information
            
        Returns:
            Dictionary with score and tier
        """
        self.logger.info(f"Scoring lead: {lead_data.get('company_name', 'Unknown')}")
        
        try:
            response = await self.provider.generate(
                prompt=scoring_prompt(lead_data)
            )
            
            result = self._parse_json_response(response.content)
            
            return {
                "score_breakdown": result.get("score_breakdown", {}),
                "ai_score": result.get("score", 0),
                "quality_tier": result.get("quality_tier", "C")
            }
            
        except Exception as e:
            self.logger.error(f"Lead scoring failed: {e}")
            return {
                "ai_score": 50,
                "quality_tier": "C",
                "score_breakdown": {"error": str(e)}
            }
    
    async def generate_email(
        self,
        lead_data: Dict[str, Any],
        email_type: str = "initial"
    ) -> Dict[str, str]:
        """Generate a personalized outreach email.
        
        Args:
            lead_data: Dictionary containing lead information
            email_type: Type of email (initial, followup_1, followup_2, etc.)
            
        Returns:
            Dictionary with subject and body
        """
        self.logger.info(f"Generating {email_type} email for {lead_data.get('company_name')}")
        
        try:
            response = await self.provider.generate(
                prompt=email_generation_prompt(lead_data, email_type)
            )
            
            return self._parse_email_response(response.content)
            
        except Exception as e:
            self.logger.error(f"Email generation failed: {e}")
            return {
                "subject": f"Quick question about {lead_data.get('company_name', 'your company')}",
                "body": f"Hi,\n\nI came across {lead_data.get('company_name')} and thought there might be an opportunity to connect.\n\nWould love to chat when you have a moment.\n\nBest regards"
            }
    
    async def detect_opportunities(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect business opportunities for a lead.
        
        Args:
            lead_data: Dictionary containing lead information
            
        Returns:
            Dictionary with opportunity analysis
        """
        self.logger.info(f"Detecting opportunities for {lead_data.get('company_name')}")
        
        try:
            response = await self.provider.generate(
                prompt=opportunity_prompt(lead_data)
            )
            
            return self._parse_json_response(response.content)
            
        except Exception as e:
            self.logger.error(f"Opportunity detection failed: {e}")
            return {
                "direct_needs": [],
                "indirect_opportunities": [],
                "timing_indicators": [],
                "competitive_landscape": "Analysis unavailable"
            }
    
    async def analyze_reply(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze an email reply.
        
        Args:
            email_data: Dictionary containing email information
            
        Returns:
            Dictionary with reply analysis
        """
        self.logger.info(f"Analyzing reply from {email_data.get('from_email')}")
        
        try:
            response = await self.provider.generate(
                prompt=reply_analysis_prompt(email_data)
            )
            
            return self._parse_json_response(response.content)
            
        except Exception as e:
            self.logger.error(f"Reply analysis failed: {e}")
            return {
                "intent": "unknown",
                "sentiment": "unknown",
                "summary": "Analysis unavailable",
                "is_interested": False
            }
    
    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON from AI response."""
        # Try to extract JSON from markdown code blocks
        json_match = None
        
        # Look for ```json blocks
        import re
        json_pattern = r'```json\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, content, re.DOTALL)
        if match:
            json_str = match.group(1)
            json_match = json_str
        else:
            # Try to find any JSON object
            json_pattern = r'\{.*\}'
            match = re.search(json_pattern, content, re.DOTALL)
            if match:
                json_str = match.group(0)
                # Find the complete JSON (handle nested braces)
                depth = 0
                for i, c in enumerate(json_str):
                    if c == '{':
                        depth += 1
                    elif c == '}':
                        depth -= 1
                        if depth == 0:
                            json_str = json_str[:i+1]
                            break
                json_match = json_str
        
        if json_match:
            try:
                return json.loads(json_match)
            except json.JSONDecodeError as e:
                self.logger.warning(f"JSON parse error: {e}")
        
        return {}
    
    def _parse_email_response(self, content: str) -> Dict[str, str]:
        """Parse email content from AI response."""
        lines = content.split("\n")
        
        subject = ""
        body_lines = []
        in_body = False
        
        for line in lines:
            stripped = line.strip()
            
            if stripped.lower().startswith("subject:"):
                subject = stripped[8:].strip().strip('"').strip("'")
                in_body = True
            elif in_body or (stripped.startswith("---") and len(stripped) == 3):
                in_body = True
                if not stripped.startswith("---"):
                    body_lines.append(line)
            elif not subject and stripped:
                body_lines.append(line)
        
        body = "\n".join(body_lines).strip()
        
        # Remove markdown formatting
        body = body.replace("**", "").replace("*", "").replace("_", "")
        
        if not subject:
            subject = "Quick question"
        
        return {"subject": subject, "body": body}
