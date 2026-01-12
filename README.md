# aitrics_assignment

aitrics 비대면 과제.

# Assume

1. client 를 web 이 아닌 EMR 로 가정. server-to-server 환경으로 가정함.
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
          "vitals": {  // MEDIUM RISK
            "HR": 80.0,
            "SBP": 125.0,
            "SpO2": 89.0
          }
        },
        {
          "recorded_at": "2025-12-01T10:15:01Z",
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

## Quick Start (Docker)

### 사전 요구사항

- Docker
- Docker Compose

### 실행 방법

```bash
# 1. 환경변수 설정
cp .env.example .env
```

`.env` 파일을 열어 `BEARER_TOKEN` 값을 설정합니다:

```
BEARER_TOKEN=my-secret-token-123
```

> 원하는 아무 문자열이나 사용 가능합니다. 이 값이 API 인증에 사용됩니다.

```bash
# 2. 서비스 시작 (DB + API 서버)
docker-compose up --build
```

> PostgreSQL과 마이그레이션이 자동으로 설정됩니다. 별도의 DB 설치가 필요 없습니다.

```bash
# 3. 서비스 종료
docker-compose down

# 볼륨까지 삭제 (DB 초기화)
docker-compose down -v
```

### API Docs + API 테스트

1. 브라우저에서 Swagger UI 접속: http://localhost:9090/docs
2. 우측 상단 **Authorize** 버튼 클릭
3. Value 입력란에 `.env`에 설정한 BEARER_TOKEN 값 입력 (예: `my-secret-token-123`)
4. **Authorize** 클릭 후 API 테스트 진행

## Local Development

### 사전 요구사항

- Python 3.13+
- PostgreSQL 16+
- [uv](https://docs.astral.sh/uv/) (Python package manager)

### 1. PostgreSQL 설정

```bash
# PostgreSQL에 접속하여 데이터베이스 생성
psql -U postgres

# DB 생성 (psql 내에서)
CREATE DATABASE vital_monitor;
CREATE DATABASE vital_monitor_test;
\q
```

### 2. 환경변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 수정합니다:

```
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/vital_monitor
TEST_DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/vital_monitor_test
BEARER_TOKEN=my-secret-token-123
```

### 3. 의존성 설치

```bash
uv sync --all-extras
```

### 4. 데이터베이스 마이그레이션

```bash
uv run alembic upgrade head
```

### 5. 서버 실행

```bash
uv run uvicorn src.app.main:app --reload
```

서버가 시작되면 http://localhost:8000/docs 에서 Swagger UI에 접속할 수 있습니다.

### 6. 테스트 실행

```bash
uv run pytest
```

### (Optional) Pre-commit Hooks 설정

```bash
uv run pre-commit install
uv run pre-commit install --hook-type pre-push
```

# Information

## DB Schema

![vital_monitor_model.png](vital_monitor_model.png)

patients 1 : N vitals 구조를 가진다.

## Optimistic DB Locking

- patients, vitals table 은 각각 version(int) table 을 가진다. (default=1)
- 고객 정보 또는 vital data 수정 시 version 을 필수값으로 받는다.
- 데이터가 업데이트되면 version 을 1씩 증가시켜 변경되었음을 알린다.
- 동시에 같은 version 을 가진 데이터가 들어오거나 과거 version 을 가진 데이터가 들어오면 먼저 들어온 요청은 처리되고 나중에 들어온 요청은 version mismatch 로 처리되지 않고 에러가
  발생한다.

## AI Development Agent

- claude_works/ 에 모든 내용이 백업됨.
- spec.md 는 과제 내용을 MD 로 export한 내용. 이것을 기준으로 해 시스템 설계 및 구현.
- CLAUDE.md와 claude_works/claude_py.md 는 작업 규칙
- vital_monitor 에서 모든 작업 계획과 주요 대화 내용을 확인할 수 있음.

### Phase 0: 설계 및 기획

가장 많은 시간을 할애. spec 을 기반으로 기술 스택을 선정하고 상세한 작업 계획을 설정.  
초기 기획 중 병렬 처리 가능한 부분을 찾아 개발 순서를 재조정하고, DB model및 코드 신뢰성을 위한 도구 추가.  
(오류) server-to-server 구성이라는 것을 생각하지 못하고 단순 web service 를 기반으로 생각해 JWT 를 도입하기로 함.  
spec을 다시 살펴보던 도중 vital data update 가 현재 예시만으로 올바르게 작동하지 않을 것을 확인, 이 부분을 수정함.  
전체 테스트 구조와 coverage목표, 테스트 케이스 등을 설정함.

### Phase 0.5: 환경 설정

linter, code formatter, type checker + pre-commit hook 도입.  
75% coverage: 개발 도중에는 coverage가 높지 않기 때문에 적당히 3/4 를 초기 값으로 설정.  
github actions 에서도 코드 검증이 필요해 CI 작업을 마지막 phase로 추가.

### Phase 1: DB Modeling

TimestampMixin 을 만들어 모든 테이블에 자동으로 created_at, updated_at 이 붙어서 작동하도록 함.  
Optimistic lock 을 위한 version 추가.  
created_at, updated_at 을 추가한 이유: 정보가 생성된 시각이 있어도 실제로 DB에 기록된 시간과 업데이트된 시각을 DB단에서 잡을 수 있다면 딜레이, 변조 확인 등에 사용 가능함.

### Phase 2, 2.5: Auth

JWT 를 적용하려다 문제를 깨닫고 서비스 구조를 server-to-server 로 정리함.  
이에 따라 굳이 JWT 를 사용할 필요가 없어져 관련된 내용을 지우고 Token 을 저장해 이를 검증하는 로직만 남김.
HMAC 등을 추가하려 했지만 server-to-server 환경에 IP whitelist 를 같이 활용하면 POST data 변조가 어려울 것이라 판단해 생략.

### Phase 3, 3.5: API Implementation

병렬 작업이 가능해 ABC 로 나누고 worktree 를 분리해 동시 작업후 main merge 를 수행.  
이후 API 문서를 다듬기 위한 작업과 전체 테스트, 리팩토링 작업을 Phase 3.5 에서 완료.  
환자와 vital data 에 대해서는 optimistic lock 이 작동하도록 신경씀.
inference 는 여러 방식이 생길 수 있기 때문에 미리 factory 와 공용 interface 를 준비해 확장을 대비. 이에 대한 내용은 Appendix 1 에 있음.  
API prefix가 v1 인 것을 보고 v2 가 생겼을 때 두 버전이 공존하며 새 버전으로 점진적으로 변경될 수 있도록 하는 API 버전 관리 전략을 고민해 Appendix 2 에 추가함.  
현재 구현이 간단한 CRUD 이기 때문에 굳이 domain entity 를 도입할 필요는 없었지만 로직 고도화 등에 대비하기 위해 코드를 남겨두고 이에 대한 도입 전략을 Appendix 3 에 추가함.

### Phase 4: Container

Docker 환경에서 간단하게 서비스를 구성할 수 있도록 dockerize 작업 수행.  
편리한 테스트를 위해 DB 를 포함하도록 구성.

### Phase 5: CI

github actions에 push 되었을 때 자동으로 코드 품질과 테스트를 검증하도록 함.  
필요 시 빌드 + 배포까지 자동화 가능.

# Appendix

## 1. Adding New Inference Strategy

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

## 2. Future: API Version Management

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

## 3. Domain Entity Strategy

### Current Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Presentation   │     │   Application   │     │ Infrastructure  │
│  (Router)       │────▶│   (Service)     │────▶│  (Repository)   │
│                 │     │                 │     │                 │
│  Schema ────────│────▶│                 │────▶│  SQLAlchemy     │
│  (Pydantic)     │     │                 │     │  Model          │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                        ┌─────────────────┐             │
                        │     Domain      │◀────────────┘
                        │   (Entity)      │  (currently not used
                        │                 │   for data transfer)
                        │  Patient, Vital │
                        └─────────────────┘
```

### Design Decision: Pragmatic Approach

This project uses SQLAlchemy models directly across layers for simplicity:

| Layer      | Current                   | Clean Architecture (Ideal)                      |
|------------|---------------------------|-------------------------------------------------|
| Router     | Returns `PatientModel`    | Returns `PatientResponse` from `Patient` entity |
| Service    | Works with `PatientModel` | Works with `Patient` entity                     |
| Repository | Returns `PatientModel`    | Converts `PatientModel` → `Patient` entity      |

**Rationale:**

- Simple CRUD operations with no complex business logic
- Reduced boilerplate (no Model ↔ Entity conversion)
- Faster development for MVP

### When to Introduce Domain Entities

Domain entities (`Patient`, `Vital`) should be actively used when:

1. **Business Logic Complexity Increases**
   ```python
   # Example: Patient entity with business rules
   @dataclass
   class Patient:
       ...
       def is_adult(self) -> bool:
           return (date.today() - self.birth_date).days >= 18 * 365

       def can_receive_treatment(self, treatment: Treatment) -> bool:
           # Complex eligibility rules
           ...
   ```

2. **Domain Events Are Needed**
   ```python
   @dataclass
   class Patient:
       ...
       events: list[DomainEvent] = field(default_factory=list)

       def admit(self):
           self.status = "admitted"
           self.events.append(PatientAdmittedEvent(self.patient_id))
   ```

3. **Multiple Persistence Mechanisms**
    - When data comes from multiple sources (DB, external API, cache)
    - Domain entity provides unified interface

4. **Testing Business Logic in Isolation**
    - Domain entities can be unit tested without DB
    - Pure Python objects with no infrastructure dependencies

### Migration Path

When complexity demands proper domain entities:

```python
# Step 1: Add conversion methods to Repository
class PatientRepository:
    async def find_by_patient_id(self, patient_id: str) -> Patient | None:
        model = await self._find_model_by_patient_id(patient_id)
        return self._to_entity(model) if model else None

    def _to_entity(self, model: PatientModel) -> Patient:
        return Patient(
            id=model.id,
            patient_id=model.patient_id,
            name=model.name,
            gender=model.gender,
            birth_date=model.birth_date,
            version=model.version,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


# Step 2: Update Service to use Domain Entity
class PatientService:
    async def get_patient(self, patient_id: str) -> Patient:
        patient = await self.repository.find_by_patient_id(patient_id)
        if patient is None:
            raise PatientNotFoundError(...)
        return patient  # Returns domain entity, not model


# Step 3: Router converts Entity → Response Schema
@router.get("/{patient_id}")
async def get_patient(...) -> PatientResponse:
    patient = await service.get_patient(patient_id)
    return PatientResponse.model_validate(patient.__dict__)
```

### Current Domain Files

Domain entities are defined but reserved for future use:

- `src/app/domain/patient.py` - Patient entity
- `src/app/domain/vital.py` - Vital entity
- `src/app/domain/exceptions.py` - Domain exceptions (actively used)
- `src/app/domain/vital_type.py` - Value object (actively used)
- `src/app/domain/risk_level.py` - Value object (actively used)
- `src/app/domain/inference/` - Inference strategy pattern (actively used)
