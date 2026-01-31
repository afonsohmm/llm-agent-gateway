import time
import google.generativeai as genai
from .base import BaseProvider
from ..api.schemas import AgentRunRequest, SuccessResponse, Result, Usage, Billing, Timing
import json

class GeminiProvider(BaseProvider):
    async def invoke(self, request: AgentRunRequest) -> SuccessResponse:
        genai.configure(api_key=request.auth.key)

        provider_start_time = time.time()

        model = genai.GenerativeModel(request.model)

        if request.input.messages:
            # Not a direct mapping, need to handle roles and content.
            # This is a simplified version.
            prompt = [f"{msg.role}: {msg.content}" for msg in request.input.messages]
            prompt = "\n".join(prompt)
        else:
            prompt = f"{request.input.instruction}\n\n{json.dumps(request.input.data) if isinstance(request.input.data, dict) else request.input.data}"
        
        generation_config = genai.types.GenerationConfig(
            temperature=request.temperature,
            max_output_tokens=request.max_output_tokens,
            top_p=request.top_p,
            stop_sequences=request.stop,
        )

        response = await model.generate_content_async(
            prompt,
            generation_config=generation_config
        )

        provider_duration_ms = int((time.time() - provider_start_time) * 1000)

        usage = self.extract_usage(response)
        
        if request.response_format == "json":
             # Gemini doesn't have a native JSON mode in the same way as OpenAI.
             # This is a simplification. We'd need to add post-processing.
            try:
                result_json = json.loads(response.text)
                result = Result(type="json", json=result_json)
            except json.JSONDecodeError:
                # Or return an error, as per requirements
                result = Result(type="text", text=response.text)
        else:
            result = Result(type="text", text=response.text)

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
        return True # But requires post-processing

    def extract_usage(self, response: any) -> dict:
        # The usage metadata from Gemini is not as straightforward as OpenAI's.
        # This is a placeholder and might need adjustment based on the actual response structure.
        # It's often not provided directly and needs to be estimated.
        return {
            "input_tokens": 0, 
            "output_tokens": 0,
            "total_tokens": 0,
            "is_estimated": True
        }