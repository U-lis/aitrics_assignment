import pytest

from app.domain.inference import BaseInference, InferenceFactory, InferenceResult, RuleBasedInference
from app.domain.risk_level import RiskLevel


class TestInferenceFactory:
    def test_get_default_strategy(self):
        """'rule_based' returns RuleBasedInference."""
        inference = InferenceFactory.get("rule_based")
        assert isinstance(inference, RuleBasedInference)

    def test_get_unknown_strategy(self):
        """Unknown name raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            InferenceFactory.get("unknown_strategy")

        assert "Unknown inference strategy: unknown_strategy" in str(exc_info.value)

    def test_register_new_strategy(self):
        """Register and use custom strategy."""

        class CustomInference(BaseInference):
            def evaluate(self, vitals: dict[str, float]) -> InferenceResult:
                return InferenceResult(1.0, RiskLevel.HIGH, ["custom_rule"])

        InferenceFactory.register("custom", CustomInference)

        inference = InferenceFactory.get("custom")
        assert isinstance(inference, CustomInference)

        result = inference.evaluate({})
        assert result.risk_score == 1.0
        assert result.risk_level == RiskLevel.HIGH
        assert result.checked_rules == ["custom_rule"]

        # Cleanup - remove custom strategy
        del InferenceFactory._strategies["custom"]
