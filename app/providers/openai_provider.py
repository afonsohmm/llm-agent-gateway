import time
from .base import BaseProvider
from ..api.schemas import AgentRunRequest, SuccessResponse, Result, Usage, Billing, Timing
from openai import AsyncOpenAI
import json

class OpenAIProvider(BaseProvider):
    async def invoke(self, request: AgentRunRequest) -> SuccessResponse:
        client = AsyncOpenAI(api_key=request.auth.key)

        provider_start_time = time.time()

        if request.input.messages:
            messages = [msg.dict() for msg in request.input.messages]
        else:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."}, 
                {"role": "user", "content": f"{request.input.instruction}\n\n{json.dumps(request.input.data) if isinstance(request.input.data, dict) else request.input.data}"}
            ]

        response_format = {"type": "json_object"} if request.response_format == "json" else {"type": "text"}
        
        completion = await client.chat.completions.create(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_output_tokens,
            top_p=request.top_p,
            stop=request.stop,
            seed=request.seed,
            response_format=response_format,
        )

        provider_duration_ms = int((time.time() - provider_start_time) * 1000)

        usage = self.extract_usage(completion)
        
        if request.response_format == "json":
            result = Result(type="json", json=json.loads(completion.choices[0].message.content))
        else:
            result = Result(type="text", text=completion.choices[0].message.content)
            
        # This is a simplified implementation. We'll add billing and other details later.
        return SuccessResponse(
            trace_id=request.trace_id,
            provider=request.provider,
            model=request.model,
            result=result,
            usage=Usage(**usage, is_estimated=False),
            billing=Billing(pricing_source="unknown"), # Placeholder
            timing=Timing(
                started_at="", # Placeholder
                ended_at="", # Placeholder
                duration_ms=0, # Placeholder
                provider_duration_ms=provider_duration_ms
            )
        )

    @property
    def supports_json_mode(self) -> bool:
        return True

    def extract_usage(self, response: any) -> dict:
        return {
            "input_tokens": response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        }