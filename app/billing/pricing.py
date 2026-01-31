from ..core.config import settings
from ..api.schemas import Usage, Billing

class PricingService:
    def __init__(self):
        self.pricing_data = settings.PRICING_DATA

    def calculate_cost(self, provider: str, model: str, usage: Usage) -> Billing:
        if not self.pricing_data:
            return Billing(pricing_source="unknown", note="Pricing data not configured.")

        provider_prices = self.pricing_data.get(provider, {})
        model_prices = provider_prices.get(model)

        if not model_prices:
            return Billing(pricing_source="unknown", note=f"Pricing for model '{model}' not configured.")

        input_cost = (usage.input_tokens / 1000) * model_prices.get("input_per_1k", 0)
        output_cost = (usage.output_tokens / 1000) * model_prices.get("output_per_1k", 0)
        
        estimated_cost = input_cost + output_cost

        return Billing(
            currency="USD",
            estimated_cost=estimated_cost,
            pricing_source="config"
        )
