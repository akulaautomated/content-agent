"""
Agent Orchestrator — the core of the AI content generation system.

How it works:
1. User sends a brief (e.g., "Write a blog post about email marketing for SaaS companies")
2. Orchestrator picks the right agent (blog_writer)
3. Agent is given a system prompt + the brief
4. Agent runs, optionally calling tools (get brand profile, analyze SEO, save draft)
5. When done, the generated content is returned and saved to the database
"""
import time
import json
from typing import Optional
from app.agents.provider import get_provider
from app.agents.personas import PERSONAS
from app.agents.tools import TOOL_DEFINITIONS, execute_tool

MAX_ITERATIONS = 10

# Map content types to agent names
CONTENT_TYPE_TO_AGENT = {
    "blog_post": "blog_writer",
    "email": "email_campaign",
    "social_post": "social_media",
    "ad_copy": "ad_copy",
    "landing_page": "landing_page",
    "case_study": "case_study",
}

# Map agent names to which tools they should have access to
AGENT_TOOLS = {
    "blog_writer": ["get_brand_profile", "analyze_seo", "save_draft", "get_keyword_suggestions"],
    "email_campaign": ["get_brand_profile", "save_draft"],
    "social_media": ["get_brand_profile", "save_draft"],
    "ad_copy": ["get_brand_profile", "save_draft"],
    "landing_page": ["get_brand_profile", "save_draft"],
    "case_study": ["get_brand_profile", "save_draft"],
    "seo_analyst": ["analyze_seo", "get_keyword_suggestions"],
    "analytics": [],
}


class AgentOrchestrator:
    def __init__(self):
        self._provider = None  # Lazy-loaded on first use

    @property
    def provider(self):
        """Only create the LLM client when we actually need it (lazy init)."""
        if self._provider is None:
            self._provider = get_provider()
        return self._provider

    async def generate(
        self,
        agent_type: str,
        task: str,
        context: dict,
    ) -> dict:
        """
        Run an agent to complete a task.

        Args:
            agent_type: Which agent to use (e.g., "blog_writer")
            task: The content brief / instructions
            context: dict with org_id, brand_id, auth_token, api_base_url

        Returns:
            dict with 'content', 'tool_uses', 'iterations', 'tokens_used', 'draft_result'
        """
        system_prompt = PERSONAS.get(agent_type)
        if not system_prompt:
            raise ValueError(f"Unknown agent type: {agent_type}. Available: {list(PERSONAS.keys())}")

        # Filter tools to only those this agent has access to
        allowed_tools = AGENT_TOOLS.get(agent_type, [])
        agent_tools = [t for t in TOOL_DEFINITIONS if t["name"] in allowed_tools]

        messages = [{"role": "user", "content": task}]
        all_tool_uses = []
        total_tokens = 0
        iterations = 0
        start_time = time.time()

        while iterations < MAX_ITERATIONS:
            iterations += 1
            response = await self.provider.generate(
                system_prompt=system_prompt,
                messages=messages,
                tools=agent_tools,
            )
            total_tokens += response.tokens_used

            if response.stop_reason == "end_turn":
                # Agent is done — return the final content
                elapsed_ms = int((time.time() - start_time) * 1000)
                return {
                    "content": response.content,
                    "tool_uses": all_tool_uses,
                    "iterations": iterations,
                    "tokens_used": total_tokens,
                    "latency_ms": elapsed_ms,
                    "draft_result": context.get("draft_result"),
                }

            elif response.stop_reason == "tool_use" and response.tool_calls:
                # Agent wants to use tools — execute them and feed results back
                tool_results = []
                for tc in response.tool_calls:
                    result = await execute_tool(tc["name"], tc["arguments"], context)
                    tool_results.append(result)
                    all_tool_uses.append({
                        "tool": tc["name"],
                        "args": tc["arguments"],
                        "result_summary": str(result)[:200],
                    })

                # Add results to messages for the next iteration
                messages = self.provider.add_tool_results_to_messages(
                    messages, response.tool_calls, tool_results
                )

        # If we hit max iterations, return whatever the last content was
        return {
            "content": "Generation reached maximum iterations. Please try with a simpler brief.",
            "tool_uses": all_tool_uses,
            "iterations": iterations,
            "tokens_used": total_tokens,
            "latency_ms": int((time.time() - start_time) * 1000),
            "draft_result": context.get("draft_result"),
        }

    def build_task_message(
        self,
        brief: str,
        content_type: str,
        tone: str,
        target_audience: Optional[str],
        keywords: list,
        platform: Optional[str],
        word_count_target: Optional[int],
        brand_id: Optional[str],
    ) -> str:
        """Build the full task message sent to the agent."""
        parts = [f"TASK: {brief}"]
        parts.append(f"\nContent Type: {content_type}")
        if platform:
            parts.append(f"Target Platform: {platform}")
        parts.append(f"Required Tone: {tone}")
        if target_audience:
            parts.append(f"Target Audience: {target_audience}")
        if keywords:
            parts.append(f"Keywords to target: {', '.join(keywords)}")
        if word_count_target:
            parts.append(f"Target word count: ~{word_count_target} words")
        if brand_id:
            parts.append(f"\nBrand Profile ID: {brand_id}")
            parts.append("Please call get_brand_profile first to understand the brand voice requirements.")
        parts.append("\nGenerate the content now. Follow your system prompt guidelines exactly.")
        return "\n".join(parts)


# Module-level singleton
orchestrator = AgentOrchestrator()
