from typing import List, Dict, Any

# System prompt for lead analysis
ANALYSIS_SYSTEM_PROMPT = """You are an expert B2B lead analyst. Your job is to analyze companies and determine:
1. If they are a good fit for outreach
2. What pain points they might have
3. What opportunities exist for value addition
4. How to personalize outreach

Be thorough, specific, and actionable in your analysis."""


# Prompt for analyzing a lead
def analysis_prompt(lead_data: Dict[str, Any]) -> str:
    return f"""Analyze this company and provide a detailed report:

Company: {lead_data.get('company_name', 'Unknown')}
Domain: {lead_data.get('domain', 'N/A')}
Description: {lead_data.get('description', 'N/A')}
Industry/Category: {lead_data.get('category', 'N/A')}
Location: {lead_data.get('city', '')}, {lead_data.get('state', '')}, {lead_data.get('country', '')}
Technologies: {', '.join(lead_data.get('technologies', [])) or 'Not detected'}
Contact Info: {lead_data.get('phone', 'N/A')}

Website Analysis:
- Title: {lead_data.get('website_title', 'N/A')}
- Meta Description: {lead_data.get('meta_description', 'N/A')}
- Headers: {lead_data.get('headers', {})}

Please provide a JSON response with:
{{
    "summary": "2-3 sentence summary of the company and their business",
    "pain_points": ["List of 3-5 potential pain points this company might have"],
    "opportunities": ["List of 3-5 business opportunities you see"],
    "recommendations": ["List of 3-5 actionable recommendations for outreach"],
    "company_size_estimate": "Estimated company size (1-10, 11-50, 51-200, 201-500, 501-1000, 1000+)",
    "industry": "Primary industry",
    "funding_stage": "Estimated funding stage if detectable",
    "personalization_hints": {{
        "opening_hook": "Something intriguing to open with",
        "recent_news": "Types of news/trends relevant to mention",
        "customization_ideas": "How to customize the outreach"
    }}
}}"""


# Prompt for email generation
def email_generation_prompt(lead_data: Dict[str, Any], email_type: str = "initial") -> str:
    tone = "professional yet friendly" if email_type == "initial" else "follow-up"
    
    return f"""Generate a personalized outreach email for this lead:

Recipient: {lead_data.get('contact_name', 'the decision maker')} at {lead_data.get('company_name', 'this company')}
Their role/title: {lead_data.get('contact_title', 'N/A')}
Company: {lead_data.get('company_name', 'Unknown')}
Company description: {lead_data.get('description', 'N/A')}
Company size: {lead_data.get('company_size_estimate', 'Unknown')}
Industry: {lead_data.get('industry', 'B2B')}

Their pain points: {', '.join(lead_data.get('pain_points', [])) or 'See attached analysis'}
Opportunities: {', '.join(lead_data.get('opportunities', [])) or 'See attached analysis'}
Personalization hints: {lead_data.get('personalization_hints', {})}

Email requirements:
- Type: {email_type} email
- Tone: {tone}
- Length: {80 if email_type == 'initial' else 50} words or less
- Include: Clear value proposition, specific reason for reaching out
- Do NOT include: Generic phrases, obvious AI-generated language
- CTA: Clear but not pushy

Return ONLY the email content (subject line + body) in this format:
---
Subject: [Your Subject Line]

[Email Body]
---"""


# Prompt for lead scoring
def scoring_prompt(lead_data: Dict[str, Any]) -> str:
    return f"""Score this lead from 0-100 based on their fit and likelihood to respond.

Company: {lead_data.get('company_name', 'Unknown')}
Domain: {lead_data.get('domain', 'N/A')}
Description: {lead_data.get('description', 'N/A')}
Industry: {lead_data.get('industry', 'N/A')}
Location: {lead_data.get('city', '')}, {lead_data.get('country', '')}
Technologies: {', '.join(lead_data.get('technologies', [])[:10]) or 'None detected'}
Has contact info: {"Yes" if lead_data.get('email') else "No"}
Has LinkedIn: {"Yes" if lead_data.get('linkedin_url') else "No"}
Has phone: {"Yes" if lead_data.get('phone') else "No"}

Provide a JSON response:
{{
    "score": 0-100,
    "quality_tier": "A (80-100) | B (60-79) | C (40-59) | D (0-39)",
    "score_breakdown": {{
        "industry_fit": {{"score": 0-25, "reason": "..."}},
        "contact_quality": {{"score": 0-25, "reason": "..."}},
        "engagement_potential": {{"score": 0-25, "reason": "..."}},
        "data_completeness": {{"score": 0-25, "reason": "..."}}
    }},
    "summary": "Brief explanation of the score"
}}"""


# Prompt for reply analysis
def reply_analysis_prompt(email_data: Dict[str, Any]) -> str:
    return f"""Analyze this email reply:

From: {email_data.get('from_email', 'N/A')}
Subject: {email_data.get('subject', 'N/A')}
Body: {email_data.get('body', 'N/A')}

Provide a JSON response:
{{
    "intent": "positive | negative | neutral | out_of_office",
    "sentiment": "positive | neutral | negative",
    "summary": "2-3 sentence summary of the reply",
    "action_items": ["What to do next"],
    "is_interested": true/false,
    "key_points": ["Important points mentioned"]
}}"""


# Opportunity detection prompt
def opportunity_prompt(lead_data: Dict[str, Any]) -> str:
    return f"""Analyze this company for business opportunities:

Company: {lead_data.get('company_name', 'Unknown')}
Industry: {lead_data.get('industry', 'Unknown')}
Technologies: {', '.join(lead_data.get('technologies', [])[:10])}
Description: {lead_data.get('description', 'N/A')}
Products/Services mentioned: {lead_data.get('products', 'N/A')}

Identify:
1. Direct needs (products/services they might need)
2. Indirect opportunities (ways to add value)
3. Timing indicators (signs of growth, change, or challenges)
4. Competitive insights (who they might be competing with)

Return JSON:
{{
    "direct_needs": ["..."],
    "indirect_opportunities": ["..."],
    "timing_indicators": ["..."],
    "competitive_landscape": "Brief overview"
}}"""
