from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.risk_level import RiskLevel


@dataclass
class InferenceResult:
    risk_score: float
    risk_level: RiskLevel
    checked_rules: list[str]


class BaseInference(ABC):
    @abstractmethod
    def evaluate(self, vitals: dict[str, float]) -> InferenceResult:
        """Evaluate vitals and return risk assessment."""
        pass
