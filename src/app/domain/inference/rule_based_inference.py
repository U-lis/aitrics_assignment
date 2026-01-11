from collections.abc import Callable

from app.domain.inference.base import BaseInference, InferenceResult
from app.domain.risk_level import RiskLevel


class RuleBasedInference(BaseInference):
    RULES: list[tuple[str, Callable[[dict[str, float]], bool]]] = [
        ("HR > 120", lambda v: v.get("HR", 0) > 120),
        ("SBP < 90", lambda v: v.get("SBP", float("inf")) < 90),
        ("SpO2 < 90", lambda v: v.get("SpO2", 100) < 90),
    ]

    def evaluate(self, vitals: dict[str, float]) -> InferenceResult:
        matched = [name for name, check in self.RULES if check(vitals)]
        count = len(matched)

        if count == 0:
            return InferenceResult(0.2, RiskLevel.LOW, matched)
        elif count == 1:
            return InferenceResult(0.5, RiskLevel.MEDIUM, matched)
        elif count == 2:
            return InferenceResult(0.7, RiskLevel.MEDIUM, matched)
        else:
            return InferenceResult(0.9, RiskLevel.HIGH, matched)
