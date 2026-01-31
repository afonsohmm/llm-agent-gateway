import pytest
import json
from app.billing.pricing import PricingService
from app.api.schemas import Usage
from app.core.config import settings

@pytest.fixture
def pricing_service(monkeypatch):
    # Mock the settings to provide a controlled pricing table by setting the JSON string
    pricing_data = {
        "openai": {
            "gpt-4o-mini": {"input_per_1k": 0.15, "output_per_1k": 0.60}
        },
        "gemini": {
            "gemini-1.5-pro": {"input_per_1k": 0.00, "output_per_1k": 0.00}
        }
    }
    monkeypatch.setattr(settings, 'PRICING_JSON', json.dumps(pricing_data))
    return PricingService()

def test_calculate_cost_openai(pricing_service):
    usage = Usage(input_tokens=1000, output_tokens=2000, total_tokens=3000, is_estimated=False)
    billing = pricing_service.calculate_cost("openai", "gpt-4o-mini", usage)
    assert billing.estimated_cost == (1 * 0.15) + (2 * 0.60)
    assert billing.pricing_source == "config"

def test_calculate_cost_unknown_model(pricing_service):
    usage = Usage(input_tokens=1000, output_tokens=2000, total_tokens=3000, is_estimated=False)
    billing = pricing_service.calculate_cost("openai", "unknown-model", usage)
    assert billing.estimated_cost is None
    assert billing.pricing_source == "unknown"

def test_calculate_cost_unknown_provider(pricing_service):
    usage = Usage(input_tokens=1000, output_tokens=2000, total_tokens=3000, is_estimated=False)
    billing = pricing_service.calculate_cost("unknown-provider", "some-model", usage)
    assert billing.estimated_cost is None
    assert billing.pricing_source == "unknown"

def test_calculate_cost_free_model(pricing_service):
    usage = Usage(input_tokens=1000, output_tokens=2000, total_tokens=3000, is_estimated=False)
    billing = pricing_service.calculate_cost("gemini", "gemini-1.5-pro", usage)
    assert billing.estimated_cost == 0
    assert billing.pricing_source == "config"
