# Phase 3C: Inference API

## Objective

Implement rule-based vital risk scoring with pluggable strategy pattern.

**Note:** This phase can run in parallel with Phase 3A and 3B.

## API

- `POST /api/v1/inference/vital-risk` - Evaluate vital risk

## Risk Rules (RuleBasedInference)

| Condition | Effect |
|-----------|--------|
| HR > 120 | Risk increase |
| SBP < 90 | Risk increase |
| SpO2 < 90 | Risk increase |

## Risk Levels

| Matched Rules | Score | Level |
|---------------|-------|-------|
| 0 | ≤0.3 | LOW |
| 1-2 | 0.4-0.7 | MEDIUM |
| ≥3 | ≥0.8 | HIGH |

## Multi-record Handling

- Evaluate each record in `records` array separately
- Return highest risk_score among all evaluations
- Include checked_rules from the record with max risk

## Tasks

### 1. Create Inference Domain (Strategy Pattern)

#### base.py
Location: `src/app/domain/inference/base.py`

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class InferenceResult:
    risk_score: float
    risk_level: str  # LOW, MEDIUM, HIGH
    checked_rules: list[str]

class BaseInference(ABC):
    @abstractmethod
    def evaluate(self, vitals: dict[str, float]) -> InferenceResult:
        """Evaluate vitals and return risk assessment"""
        pass
```

#### rule_based_inference.py
Location: `src/app/domain/inference/rule_based_inference.py`

```python
class RuleBasedInference(BaseInference):
    RULES = [
        ("HR > 120", lambda v: v.get("HR", 0) > 120),
        ("SBP < 90", lambda v: v.get("SBP", float("inf")) < 90),
        ("SpO2 < 90", lambda v: v.get("SpO2", 100) < 90),
    ]

    def evaluate(self, vitals: dict[str, float]) -> InferenceResult:
        matched = [name for name, check in self.RULES if check(vitals)]
        count = len(matched)

        if count == 0:
            return InferenceResult(0.2, "LOW", matched)
        elif count == 1:
            return InferenceResult(0.5, "MEDIUM", matched)
        elif count == 2:
            return InferenceResult(0.7, "MEDIUM", matched)
        else:  # count >= 3
            return InferenceResult(0.9, "HIGH", matched)
```

#### factory.py
Location: `src/app/domain/inference/factory.py`

```python
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
    def register(cls, name: str, strategy: type[BaseInference]):
        """Register a new inference strategy for future use"""
        cls._strategies[name] = strategy
```

### 2. Create Inference Schemas

Location: `src/app/presentation/schemas/inference_schema.py`

```python
class VitalRecord(BaseModel):
    recorded_at: datetime
    vitals: dict[str, float]  # e.g., {"HR": 130.0, "SBP": 85.0}

class InferenceRequest(BaseModel):
    patient_id: str
    records: list[VitalRecord]

class InferenceResponse(BaseModel):
    patient_id: str
    risk_score: float
    risk_level: str
    checked_rules: list[str]
    evaluated_at: datetime
```

### 3. Create InferenceService

Location: `src/app/application/inference_service.py`

```python
class InferenceService:
    def __init__(self, strategy_name: str = "rule_based"):
        self.inference = InferenceFactory.get(strategy_name)

    def evaluate(self, request: InferenceRequest) -> InferenceResponse:
        max_result = None

        for record in request.records:
            result = self.inference.evaluate(record.vitals)
            if max_result is None or result.risk_score > max_result.risk_score:
                max_result = result

        return InferenceResponse(
            patient_id=request.patient_id,
            risk_score=max_result.risk_score,
            risk_level=max_result.risk_level,
            checked_rules=max_result.checked_rules,
            evaluated_at=datetime.utcnow()
        )
```

### 4. Create Inference Router

Location: `src/app/presentation/inference_router.py`

```python
router = APIRouter(prefix="/api/v1/inference", tags=["inference"])

@router.post("/vital-risk", response_model=InferenceResponse)
async def evaluate_vital_risk(
    request: InferenceRequest,
    doctor: Doctor = Depends(get_current_doctor),  # Auth required
):
    service = InferenceService()
    return service.evaluate(request)
```

## Checklist

- [ ] BaseInference ABC created
- [ ] InferenceResult dataclass created
- [ ] RuleBasedInference implemented
- [ ] InferenceFactory created
- [ ] Inference schemas created
- [ ] InferenceService with multi-record handling
- [ ] Inference router created
- [ ] Auth dependency applied
- [ ] Returns max risk_score among records

## Test Cases (TBD)

To be discussed with user.
