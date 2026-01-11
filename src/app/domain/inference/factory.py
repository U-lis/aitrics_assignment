from app.domain.inference.base import BaseInference
from app.domain.inference.rule_based_inference import RuleBasedInference


class InferenceFactory:
    _strategies: dict[str, type[BaseInference]] = {
        "rule_based": RuleBasedInference,
    }

    @classmethod
    def get(cls, strategy_name: str = "rule_based") -> BaseInference:
        strategy_class = cls._strategies.get(strategy_name)
        if not strategy_class:
            raise ValueError(f"Unknown inference strategy: {strategy_name}")
        return strategy_class()

    @classmethod
    def register(cls, name: str, strategy: type[BaseInference]) -> None:
        """Register a new inference strategy for future use."""
        cls._strategies[name] = strategy
