"""
Agent Orchestrator

Routes tasks to appropriate AI agents for content generation.
Handles task execution and result aggregation.
"""
from app.config import settings
from openai import AsyncOpenAI


class AgentOrchestrator:
    """Manages agent routing and execution."""

    def __init__(self):
        self._client = None
        self.model = settings.llm_model

    @property
    def client(self):
        """Lazy-load the OpenAI client on first access."""
        if self._client is None:
            self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        return self._client

    async def generate(self, agent_type: str, task: str, context: dict = None):
        """
        Generate content using the specified agent.

        Args:
            agent_type: Type of agent (blog_writer, social_post, email, etc.)
            task: The task/prompt for content generation
            context: Additional context (org_id, brand_id, content_type, etc.)

        Returns:
            dict with keys: result, tokens_used, model
        """
        if context is None:
            context = {}

        # Map agent types to system prompts
        system_prompts = {
            "blog_writer": """You are an expert blog writer for a digital marketing agency.
Write engaging, SEO-optimized blog posts that are 1500-2500 words long.
Include proper heading structure, meta descriptions, and internal linking suggestions.
Maintain a professional but conversational tone.""",

            "social_post": """You are a social media expert. Create platform-optimized posts.
Match the tone and format to the specific platform.
Include relevant hashtags and emojis.
Keep content engaging and shareable.""",

            "email": """You are an email marketing expert.
Write compelling email subject lines and body copy.
Focus on conversions and engagement.
Use persuasive copywriting techniques.""",

            "ad_copy": """You are an advertising copywriter.
Write concise, compelling ad copy for digital platforms.
Follow character limits for the platform (Google Ads, Meta, LinkedIn).
Include clear CTAs and value propositions.""",

            "landing_page": """You are a conversion copywriter.
Write landing page copy that converts visitors into customers.
Structure the page with hero section, benefits, social proof, and CTA.
Use psychological triggers and persuasion principles.""",

            "case_study": """You are a case study writer.
Write compelling case studies following the Challenge-Solution-Results framework.
Include specific metrics and data points.
Make it relatable and credible.""",
        }

        system_prompt = system_prompts.get(agent_type, system_prompts["blog_writer"])

        try:
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": task},
                ],
                temperature=0.7,
                max_tokens=2000,
            )

            # Extract result
            generated_content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            return {
                "result": generated_content,
                "tokens_used": tokens_used,
                "model": self.model,
            }

        except Exception as e:
            # Return error result
            return {
                "result": f"Error generating content: {str(e)}",
                "tokens_used": 0,
                "model": self.model,
                "error": str(e),
            }


# Global orchestrator instance
orchestrator = AgentOrchestrator()
