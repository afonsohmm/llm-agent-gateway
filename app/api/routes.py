from fastapi import APIRouter, Request, HTTPException
from ..api.schemas import AgentRunRequest, SuccessResponse, ErrorResponse
from ..agents.agent_service import AgentService
from ..core.errors import ValidationException, ProviderException
from ..core.config import settings
from ..providers.factory import get_provider
from typing import Union, List
import time
import datetime

router = APIRouter()

@router.post("/v1/agent:run", response_model=Union[SuccessResponse, ErrorResponse])
async def agent_run(request: AgentRunRequest, http_request: Request):
    # ... (existing agent_run implementation)
    trace_id = http_request.state.trace_id
    request.trace_id = trace_id
    
    start_time = time.time()
    started_at = datetime.datetime.utcnow().isoformat()

    try:
        if not request.input.messages and not request.input.instruction:
            raise ValidationException("Either 'messages' or 'instruction' must be provided.")

        response = await AgentService.run_agent(request)
        
        duration_ms = int((time.time() - start_time) * 1000)
        response.timing.started_at = started_at
        response.timing.ended_at = datetime.datetime.utcnow().isoformat()
        response.timing.duration_ms = duration_ms

        return response

    except (ValidationException, ProviderException) as e:
        raise e
    except Exception as e:
        raise ProviderException(str(e))


@router.get("/health")
async def health():
    return {"status": "ok"}

@router.get("/ready")
async def ready():
    """
    Readiness probe. Checks if critical configurations are loaded.
    """
    if not settings.PRICING_JSON or settings.PRICING_DATA is None:
        raise HTTPException(status_code=503, detail="Pricing configuration not loaded.")
    
    # Optionally, add a check for Ollama connection if it's a hard dependency
    # ...

    return {"status": "ready"}

@router.get("/v1/providers")
async def list_providers():
    """
    Dynamically lists available providers and their capabilities.
    """
    # This is a bit of a hack. A better way would be to register providers.
    provider_names = ["openai", "gemini", "ollama"]
    providers_info = []
    for name in provider_names:
        try:
            provider = get_provider(name)
            capabilities = []
            if provider.supports_json_mode:
                capabilities.append("json_mode")
            
            # This is a simplification, we assume all support chat completions for now
            capabilities.append("chat_completions")

            providers_info.append({"name": name, "capabilities": capabilities})
        except ValueError:
            # Provider not implemented or misconfigured
            pass
    return {"providers": providers_info}
