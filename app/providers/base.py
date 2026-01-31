from abc import ABC, abstractmethod
from ..api.schemas import AgentRunRequest, SuccessResponse

class BaseProvider(ABC):
    @abstractmethod
    async def invoke(self, request: AgentRunRequest) -> SuccessResponse:
        pass

    @property
    @abstractmethod
    def supports_json_mode(self) -> bool:
        pass

    @abstractmethod
    def extract_usage(self, response: any) -> dict:
        pass
