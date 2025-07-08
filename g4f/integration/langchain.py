from __future__ import annotations

from typing import Any, Dict
from langchain_community.chat_models import openai
from langchain_community.chat_models.openai import ChatOpenAI, BaseMessage, convert_message_to_dict
from pydantic import Field
import httpx

# Removed custom new_convert_message_to_dict and monkeypatching

class ChatAI(ChatOpenAI):
    model_name: str = Field(default="gpt-4o", alias="model")

    @classmethod
    def validate_environment(cls, values: dict) -> dict:
        # Define a sync client that calls Pollinations API
        def pollinations_sync(messages, model="gpt-4o", **kwargs):
            payload = {
                "model": model,
                "messages": messages,
                "stream": False
            }
            try:
                response = httpx.post(
                    "https://text.pollinations.ai/openai",
                    json=payload,
                    headers={"Content-Type": "application/json", "referer": "https://pollinations.ai/"},
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
                if "choices" in data and data["choices"]:
                    return data
                else:
                    return {"choices": [{"message": {"role": "assistant", "content": "No response from Pollinations API."}}]}
            except Exception as e:
                return {"choices": [{"message": {"role": "assistant", "content": f"Pollinations API error: {e}"}}]}

        # Define an async client that calls Pollinations API
        async def pollinations_async(messages, model="gpt-4o", **kwargs):
            payload = {
                "model": model,
                "messages": messages,
                "stream": False
            }
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://text.pollinations.ai/openai",
                        json=payload,
                        headers={"Content-Type": "application/json", "referer": "https://pollinations.ai/"},
                        timeout=30
                    )
                    response.raise_for_status()
                    data = response.json()
                    if "choices" in data and data["choices"]:
                        return data
                    else:
                        return {"choices": [{"message": {"role": "assistant", "content": "No response from Pollinations API."}}]}
            except Exception as e:
                return {"choices": [{"message": {"role": "assistant", "content": f"Pollinations API error: {e}"}}]}

        class PollinationsClient:
            def __init__(self, sync_func):
                self.sync_func = sync_func
            def create(self, *args, **kwargs):
                return self.sync_func(*args, **kwargs)

        class PollinationsAsyncClient:
            def __init__(self, async_func):
                self.async_func = async_func
            async def create(self, *args, **kwargs):
                return await self.async_func(*args, **kwargs)

        values["client"] = PollinationsClient(pollinations_sync)
        values["async_client"] = PollinationsAsyncClient(pollinations_async)
        return values