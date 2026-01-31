import time
import httpx
import json
from .base import BaseProvider
from ..api.schemas import AgentRunRequest, SuccessResponse, Result, Usage, Billing, Timing
from ..core.config import settings

class OllamaProvider(BaseProvider):
    async def invoke(self, request: AgentRunRequest) -> SuccessResponse:
        async with httpx.AsyncClient() as client:
            provider_start_time = time.time()

            if request.input.messages:
                messages = [msg.dict() for msg in request.input.messages]
            else:
                messages = [
                    {"role": "system", "content": "You are a helpful assistant."}, 
                    {"role": "user", "content": f"{request.input.instruction}\n\n{json.dumps(request.input.data) if isinstance(request.input.data, dict) else request.input.data}"}
                ]
            
            response_format = "json" if request.response_format == "json" else ""

            payload = {
                "model": request.model,
                "messages": messages,
                "stream": False,
                "format": response_format,
                "options": {
                    "temperature": request.temperature,
                    "top_p": request.top_p,
                    "stop": request.stop,
                    "seed": request.seed,
                }
            }

            res = await client.post(
                f"{settings.OLLAMA_BASE_URL}/api/chat",
                json=payload,
                timeout=request.timeout_seconds or settings.REQUEST_TIMEOUT_SECONDS
            )
            res.raise_for_status()
            ollama_response = res.json()

            provider_duration_ms = int((time.time() - provider_start_time) * 1000)

            usage = self.extract_usage(ollama_response)

            if request.response_format == "json":
                result = Result(type="json", json=json.loads(ollama_response["message"]["content"]))
            else:
                result = Result(type="text", text=ollama_response["message"]["content"])
            
            # This is a simplified implementation. We'll add billing and other details later.
            return SuccessResponse(
                trace_id=request.trace_id,
                provider=request.provider,
                model=request.model,
                result=result,
                usage=Usage(**usage),
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
        # Ollama provides usage data in the response
        return {
            "input_tokens": response.get("prompt_eval_count", 0),
            "output_tokens": response.get("eval_count", 0),
            "total_tokens": response.get("prompt_eval_count", 0) + response.get("eval_count", 0),
            "is_estimated": False,
        }