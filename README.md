# aitrics_assignment
aitrics 비대면 과제.

# Assume
1. client 가 web 이 아닌 EMR 로 가정 server-to-server 환경으로 가정함.
2. vital 교정 API의 request 에 없는 값이 있어 이를 추가함.
    - 원본
    ```json
    {
        "value": 115.0,
        "version": 2
    }
    ```
   - 실제 구현
   ```json
   {
       "vital_type": "HR",
       "value": 115.0,
       "version": 2
   }
   ```
   
3. Inference API 의 input 이 list type 인데 여러 값이 들어온 경우에 대한 처리 규칙이 없어 최대 위험도를 사용함.
    - 예시 입력
    ```json5
    {
      "patient_id": "P00001234",
      "records": [
        {
          "recorded_at": "2025-12-01T10:15:00Z",
          "vitals": {  // MED RISK
            "HR": 80.0,
            "SBP": 125.0,
            "SpO2": 89.0
          }
        },
        {
          "recorded_at": "2025-12-01T10:15:00Z",
          "vitals": {  // HIGH RISK
            "HR": 140.0,
            "SBP": 75.0,
            "SpO2": 84.0
          }
        }
      ]
    }
    ```
   - 예시 출력 : 더 높은 값 기준으로 응답
    ```json5
    {
     "patient_id": "P00001234",
     "risk_score": 0.91,
     "risk_level": "HIGH",
     "checked_rules": ["HR > 120", "SBP < 90", "SpO2 < 90"],
     "evaluated_at": "2025-12-01T10:20:00Z"
    }
    ```   
   
## Modifications
1. 2.2 Vital data API 의 api prefix 가 통일되지 않음. prefix를 통일하기 위해 Vital 데이터 조회 API 를 변경함.
    - 원본 : `/api/v1/patients/{patient_id}/vitals`
    - 수정 : `/api/v1/vitals/patient/{patient_id}`
   
# How to use

## Environment Setup

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env` and set your values:

### Database URL
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/vital_monitor
TEST_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/vital_monitor_test
```

### JWT Secret Key
Generate a secure random key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### AES-256 Secret Key (32 bytes)
Generate a 32-byte key for AES-256 encryption:
```python
import os
import base64

# Generate 32 random bytes
key = os.urandom(32)

# Encode to base64 for storage in .env
encoded_key = base64.b64encode(key).decode('utf-8')
print(encoded_key)
```

Or use one-liner:
```bash
python -c "import os, base64; print(base64.b64encode(os.urandom(32)).decode())"
```

## Install Dependencies
```bash
uv sync --all-extras
```

## Run Pre-commit Hooks Setup
```bash
uv run pre-commit install
uv run pre-commit install --hook-type pre-push
```

## Adding New Inference Strategy

The inference system uses the Strategy Pattern, making it easy to add new risk evaluation methods.

### Step 1: Create a new strategy class

Create a new file in `src/app/domain/inference/` that extends `BaseInference`:

```python
# src/app/domain/inference/ml_inference.py
from app.domain.inference.base import BaseInference, InferenceResult
from app.domain.risk_level import RiskLevel


class MLInference(BaseInference):
    def __init__(self):
        # Load your ML model here
        self.model = self._load_model()

    def _load_model(self):
        # Model loading logic
        pass

    def evaluate(self, vitals: dict[str, float]) -> InferenceResult:
        # Your inference logic here
        score = self.model.predict(vitals)

        if score < 0.4:
            level = RiskLevel.LOW
        elif score < 0.8:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.HIGH

        return InferenceResult(
            risk_score=score,
            risk_level=level,
            checked_rules=["ml_model_v1"],  # or relevant features
        )
```

### Step 2: Register the strategy

Option A: Register at module load (recommended for built-in strategies)

```python
# src/app/domain/inference/factory.py
from app.domain.inference.ml_inference import MLInference

class InferenceFactory:
    _strategies: dict[str, type[BaseInference]] = {
        "rule_based": RuleBasedInference,
        "ml": MLInference,  # Add here
    }
```

Option B: Register dynamically at runtime

```python
from app.domain.inference import InferenceFactory, MLInference

InferenceFactory.register("ml", MLInference)
```

### Step 3: Use the new strategy

```python
from app.application.inference_service import InferenceService

# Use the new strategy
service = InferenceService(strategy_name="ml")
response = service.evaluate(request)
```

### Strategy Interface

All strategies must implement:

```python
class BaseInference(ABC):
    @abstractmethod
    def evaluate(self, vitals: dict[str, float]) -> InferenceResult:
        """
        Args:
            vitals: Dictionary of vital signs (e.g., {"HR": 80.0, "SBP": 120.0})

        Returns:
            InferenceResult with risk_score (0.0-1.0), risk_level, and checked_rules
        """
        pass
```

## Future: API Version Management

When v2 API is needed, consider the following structure options:

### Option A: Directory-based separation

```
src/app/presentation/
├── api/
│   ├── v1/
│   │   ├── __init__.py          # v1_router assembly
│   │   ├── patient_router.py    # prefix="/patients"
│   │   ├── vital_router.py      # prefix="/vitals"
│   │   └── inference_router.py  # prefix="/inference"
│   └── v2/
│       ├── __init__.py          # v2_router assembly
│       └── ...
└── schemas/                      # Shared (version-agnostic)
```

```python
# main.py
from app.presentation.api.v1 import v1_router
from app.presentation.api.v2 import v2_router

app.include_router(v1_router, prefix="/api/v1")
app.include_router(v2_router, prefix="/api/v2")
```

**Pros:** Clear separation, v1/v2 independent development
**Cons:** File relocation required, deeper directory nesting

### Option B: Central router assembly

```
src/app/presentation/
├── v1.py                        # v1_router assembly
├── v2.py                        # v2_router assembly
├── routers/
│   ├── patient_router.py        # prefix="/patients"
│   ├── vital_router.py
│   └── inference_router.py
└── schemas/
```

```python
# v1.py
v1_router = APIRouter()
v1_router.include_router(patient_router)
v1_router.include_router(vital_router)
v1_router.include_router(inference_router)
```

**Pros:** Minimal file changes, routers can be reused across versions
**Cons:** Less clear separation between versions
