"""
LLM Provider abstraction.
Supports OpenAI (default) and Anthropic.
Switch by setting LLM_PROVIDER=anthropic in .env
"""
from __future__ import annotations
import json
from typing import Any
from app.config import settings


class LLMResponse:
    """Unified response object regardless of which provider generated it."""
    def __init__(self, content: str, tool_calls: list, stop_reason: str, tokens_used: int):
        self.content = content
        self.tool_calls = tool_calls   # list of {"name": ..., "arguments": {...}, "call_id": ...}
        self.stop_reason = stop_reason  # "end_turn" or "tool_use"
        self.tokens_used = tokens_used


class OpenAIProvider:
    """Uses OpenAI function calling (GPT-4o, GPT-4.1, etc.)"""

    def __init__(self):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.llm_model

    async def generate(self, system_prompt: str, messages: list, tools: list) -> LLMResponse:
        # Convert tool definitions to OpenAI's function format
        oai_tools = [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["input_schema"],
                },
            }
            for t in tools
        ] if tools else []

        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": [{"role": "system", "content": system_prompt}] + messages,
        }
        if oai_tools:
            kwargs["tools"] = oai_tools

        response = await self.client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        msg = choice.message

        # Extract tool calls if any
        tool_calls = []
        if msg.tool_calls:
            for tc in msg.tool_calls:
                tool_calls.append({
                    "name": tc.function.name,
                    "arguments": json.loads(tc.function.arguments),
                    "call_id": tc.id,
                })

        stop_reason = "tool_use" if tool_calls else "end_turn"
        tokens_used = response.usage.total_tokens if response.usage else 0

        return LLMResponse(
            content=msg.content or "",
            tool_calls=tool_calls,
            stop_reason=stop_reason,
            tokens_used=tokens_used,
        )

    def add_tool_results_to_messages(self, messages: list, tool_calls: list, results: list) -> list:
        """Append tool results in the format OpenAI expects."""
        # Add the assistant message that triggered the tool calls
        messages.append({
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": tc["call_id"],
                    "type": "function",
                    "function": {"name": tc["name"], "arguments": json.dumps(tc["arguments"])},
                }
                for tc in tool_calls
            ],
        })
        # Add each tool result
        for tc, result in zip(tool_calls, results):
            messages.append({
                "role": "tool",
                "tool_call_id": tc["call_id"],
                "content": json.dumps(result),
            })
        return messages


class AnthropicProvider:
    """Uses Anthropic tool use (Claude Sonnet, Opus, etc.)"""

    def __init__(self):
        import anthropic
        self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = settings.llm_model

    async def generate(self, system_prompt: str, messages: list, tools: list) -> LLMResponse:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": 4096,
            "system": system_prompt,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools

        response = await self.client.messages.create(**kwargs)

        content_text = ""
        tool_calls = []
        for block in response.content:
            if block.type == "text":
                content_text = block.text
            elif block.type == "tool_use":
                tool_calls.append({
                    "name": block.name,
                    "arguments": block.input,
                    "call_id": block.id,
                })

        stop_reason = "tool_use" if response.stop_reason == "tool_use" else "end_turn"
        tokens_used = response.usage.input_tokens + response.usage.output_tokens

        return LLMResponse(
            content=content_text,
            tool_calls=tool_calls,
            stop_reason=stop_reason,
            tokens_used=tokens_used,
        )

    def add_tool_results_to_messages(self, messages: list, tool_calls: list, results: list) -> list:
        """Append tool results in the format Anthropic expects."""
        messages.append({
            "role": "assistant",
            "content": [
                {"type": "tool_use", "id": tc["call_id"], "name": tc["name"], "input": tc["arguments"]}
                for tc in tool_calls
            ],
        })
        messages.append({
            "role": "user",
            "content": [
                {"type": "tool_result", "tool_use_id": tc["call_id"], "content": json.dumps(result)}
                for tc, result in zip(tool_calls, results)
            ],
        })
        return messages


def get_provider() -> OpenAIProvider | AnthropicProvider:
    """Factory: returns the right provider based on LLM_PROVIDER env var."""
    if settings.llm_provider == "anthropic":
        return AnthropicProvider()
    return OpenAIProvider()
