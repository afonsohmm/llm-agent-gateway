from ..api.schemas import AgentRunRequest, SuccessResponse, Usage
from ..providers.factory import get_provider
from .prompts import construct_prompt
from ..billing.pricing import PricingService
from ..utils.token_estimator import estimate_tokens
import uuid

class AgentService:
    @staticmethod
    async def run_agent(request: AgentRunRequest) -> SuccessResponse:
        pricing_service = PricingService()

        # 1. Get the provider
        provider = get_provider(request.provider)

        # 2. Construct the prompt if not in message format
        if not request.input.messages:
            request.input.messages = construct_prompt(
                instruction=request.input.instruction,
                data=request.input.data,
                provider=request.provider,
                response_format=request.response_format,
                json_schema=request.json_schema
            )
        
        # 3. Add trace_id to the request
        if not request.trace_id:
            request.trace_id = str(uuid.uuid4())

        # 4. Invoke the provider
        response = await provider.invoke(request)

        # 5. Estimate tokens if necessary
        if response.usage.is_estimated:
            # A more robust implementation would estimate input and output separately
            input_tokens = estimate_tokens(request.input)
            output_tokens = estimate_tokens(response.result.text or response.result.json)
            response.usage = Usage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                is_estimated=True
            )

        # 6. Calculate billing
        response.billing = pricing_service.calculate_cost(
            provider=request.provider,
            model=request.model,
            usage=response.usage
        )
        
        return response
