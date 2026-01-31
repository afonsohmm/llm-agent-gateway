from pydantic import BaseModel, Field, conlist
from typing import Literal, Union, Optional, List, Dict, Any

# Generic Models
class Auth(BaseModel):
    type: Literal["bearer", "api_key", "none"]
    key: Optional[str] = None

class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class Input(BaseModel):
    instruction: Optional[str] = None
    data: Optional[Union[Dict, str]] = None
    messages: Optional[conlist(Message, min_length=1)] = None

class AgentRunRequest(BaseModel):
    provider: Literal["openai", "gemini", "ollama"]
    model: str
    auth: Auth
    input: Input
    response_format: Literal["text", "json"] = "text"
    temperature: Optional[float] = Field(0.2, ge=0, le=2)
    max_output_tokens: Optional[int] = None
    top_p: Optional[float] = None
    stop: Optional[List[str]] = None
    seed: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    json_schema: Optional[Dict[str, Any]] = None
    strict_json: bool = True
    trace_id: Optional[str] = None
    timeout_seconds: Optional[int] = None
    safe_mode: bool = True

class Result(BaseModel):
    type: Literal["text", "json"]
    text: Optional[str] = None
    json: Optional[Dict[str, Any]] = None

class Usage(BaseModel):
    input_tokens: int
    output_tokens: int
    total_tokens: int
    is_estimated: bool = False

class Billing(BaseModel):
    currency: str = "USD"
    estimated_cost: Optional[float] = None
    pricing_source: Literal["config", "unknown"]
    note: Optional[str] = None

class Timing(BaseModel):
    started_at: str
    ended_at: str
    duration_ms: int
    provider_duration_ms: int

class Warning(BaseModel):
    code: str
    message: str

class Echo(BaseModel):
    metadata: Optional[Dict[str, Any]] = None

class SuccessResponse(BaseModel):
    ok: bool = True
    trace_id: str
    provider: str
    model: str
    result: Result
    usage: Usage
    billing: Billing
    timing: Timing
    warnings: List[Warning] = []
    echo: Optional[Echo] = None

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    ok: bool = False
    trace_id: str
    error: ErrorDetail
