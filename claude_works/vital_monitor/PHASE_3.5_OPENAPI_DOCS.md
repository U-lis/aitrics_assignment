# Phase 3.5: OpenAPI Documentation

## Objective

Update OpenAPI documentation for all Phase 3ABC APIs so that a frontend developer with no prior API knowledge can integrate using only Swagger/ReDoc documentation.

## Prerequisites

- Phase 3A (Patient API): Completed
- Phase 3B (Vital API): Completed
- Phase 3C (Inference API): Completed

## Current State

| Component | Status |
|-----------|--------|
| FastAPI app metadata | Basic (title, description, version only) |
| Security scheme | Uses HTTPBearer but not declared in OpenAPI tags |
| Endpoint docstrings | None |
| Schema Field descriptions | None |
| Response examples | None |
| Error response documentation | Not in OpenAPI (handled via exception handlers only) |

## Files to Modify

| File | Changes |
|------|---------|
| `src/app/presentation/schemas/error_schema.py` | **NEW**: Shared error response schema |
| `src/app/main.py` | Add `openapi_tags` metadata |
| `src/app/presentation/schemas/patient_schema.py` | Add Field descriptions and examples |
| `src/app/presentation/schemas/vital_schema.py` | Add Field descriptions and examples |
| `src/app/presentation/schemas/inference_schema.py` | Add Field descriptions and examples |
| `src/app/presentation/patient_router.py` | Add endpoint docs and error responses |
| `src/app/presentation/vital_router.py` | Add endpoint docs and error responses |
| `src/app/presentation/inference_router.py` | Add endpoint docs and error responses |

---

## Task 1: Foundation

### 1.1 Create Error Response Schema

Create `src/app/presentation/schemas/error_schema.py`:

```python
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response format for all API errors."""

    detail: str = Field(
        ...,
        description="Error message describing what went wrong",
        examples=["Patient P00001234 not found"]
    )
```

### 1.2 Update main.py

Add `openapi_tags` to FastAPI instantiation in `src/app/main.py`:

```python
openapi_tags = [
    {
        "name": "patients",
        "description": "Patient registration and management. Supports optimistic locking for updates.",
    },
    {
        "name": "vitals",
        "description": "Vital signs data recording, retrieval, and correction. Supports optimistic locking for updates.",
    },
    {
        "name": "inference",
        "description": "Rule-based risk assessment using vital signs data.",
    },
]

app = FastAPI(
    title="Vital Monitor API",
    description="Hospital Vital Signs Monitoring REST API",
    version="0.1.0",
    openapi_tags=openapi_tags,
)
```

---

## Task 2: Patient Documentation

### 2.1 Update patient_schema.py

Add Field descriptions and examples to all schema classes.

**PatientCreateRequest fields:**
- `patient_id`: Hospital patient identifier (e.g., "P00001234")
- `name`: Patient full name
- `gender`: "M" for male, "F" for female
- `birth_date`: Date of birth (YYYY-MM-DD)

**PatientUpdateRequest fields:**
- Same as above + `version`: Current version number for optimistic locking

**PatientResponse fields:**
- Add descriptions to all fields
- Add `model_config.json_schema_extra` with complete example

**Example values (from spec.md):**
```json
{
  "patient_id": "P00001234",
  "name": "Hong Gil-dong",
  "gender": "M",
  "birth_date": "1975-03-01"
}
```

### 2.2 Update patient_router.py

**POST /api/v1/patients (register_patient):**
- summary: "Register a new patient"
- description: "Creates a new patient record in the hospital system."
- responses:
  - 401: {"model": ErrorResponse, "description": "Invalid or missing Bearer token"}
  - 409: {"model": ErrorResponse, "description": "Patient with this patient_id already exists"}

**PUT /api/v1/patients/{patient_id} (update_patient):**
- summary: "Update patient information"
- description: "Updates an existing patient record. Requires version field for optimistic locking to prevent concurrent modification conflicts."
- Add Path parameter description for `patient_id`
- responses:
  - 401: {"model": ErrorResponse, "description": "Invalid or missing Bearer token"}
  - 404: {"model": ErrorResponse, "description": "Patient not found"}
  - 409: {"model": ErrorResponse, "description": "Version mismatch - record was modified by another request"}

---

## Task 3: Vital Documentation

### 3.1 Update vital_schema.py

Add Field descriptions including units where applicable.

**VitalCreateRequest fields:**
- `patient_id`: Hospital patient identifier
- `recorded_at`: When the vital sign was recorded (ISO 8601 datetime with timezone)
- `vital_type`: Type of vital sign (HR, RR, SBP, DBP, SpO2, BT)
- `value`: Measured value (unit depends on vital_type)

**VitalUpdateRequest fields:**
- `value`: Corrected measurement value
- `vital_type`: Type of vital sign
- `version`: Current version for optimistic locking

**VitalResponse, VitalItem, VitalListResponse:**
- Add descriptions to all fields
- Add examples

**Vital type units (include in vital_type description):**
- HR: bpm (beats per minute)
- RR: breaths/min
- SBP/DBP: mmHg
- SpO2: %
- BT: Celsius

### 3.2 Update vital_router.py

**POST /api/v1/vitals (create_vital):**
- summary: "Record vital sign data"
- description: "Records a single vital sign measurement for a patient. Patient must exist."
- responses:
  - 401: {"model": ErrorResponse, "description": "Invalid or missing Bearer token"}
  - 404: {"model": ErrorResponse, "description": "Patient not found"}

**GET /api/v1/vitals/patient/{patient_id} (get_vitals):**
- summary: "Query vital records by time range"
- description: "Retrieves vital records for a patient within specified time range. Optionally filter by vital type."
- Add Path parameter description: `patient_id`
- Add Query parameter descriptions:
  - `from`: Start of time range, inclusive (ISO 8601)
  - `to`: End of time range, inclusive (ISO 8601)
  - `vital_type`: Optional filter by vital type
- responses:
  - 401: {"model": ErrorResponse, "description": "Invalid or missing Bearer token"}

**PUT /api/v1/vitals/{vital_id} (update_vital):**
- summary: "Correct vital record"
- description: "Updates a vital record value. Requires version field for optimistic locking."
- Add Path parameter description: `vital_id` (UUID of the vital record)
- responses:
  - 401: {"model": ErrorResponse, "description": "Invalid or missing Bearer token"}
  - 404: {"model": ErrorResponse, "description": "Vital record not found"}
  - 409: {"model": ErrorResponse, "description": "Version mismatch - record was modified by another request"}

---

## Task 4: Inference Documentation

### 4.1 Update inference_schema.py

**VitalRecord fields:**
- `recorded_at`: Timestamp when these vitals were recorded
- `vitals`: Dictionary mapping vital type to measured value (e.g., {"HR": 130.0, "SBP": 85.0})

**InferenceRequest fields:**
- `patient_id`: Patient identifier for the inference request
- `records`: List of vital records to evaluate (minimum 1 record required)

**InferenceResponse fields:**
- `patient_id`: Patient identifier
- `risk_score`: Calculated risk score (0.0 to 1.0)
- `risk_level`: Risk category (LOW, MEDIUM, HIGH)
- `checked_rules`: List of triggered risk rules
- `evaluated_at`: Timestamp of evaluation

Add complete example matching spec.md:
```json
{
  "patient_id": "P00001234",
  "risk_score": 0.91,
  "risk_level": "HIGH",
  "checked_rules": ["HR > 120", "SBP < 90", "SpO2 < 90"],
  "evaluated_at": "2025-12-01T10:20:00Z"
}
```

### 4.2 Update inference_router.py

**POST /api/v1/inference/vital-risk (evaluate_vital_risk):**
- summary: "Evaluate vital-based risk score"
- description: Multi-line description including:
  ```
  Evaluates patient vital signs for risk assessment using rule-based inference.

  **Risk Rules:**
  - HR > 120: Elevated heart rate
  - SBP < 90: Low blood pressure
  - SpO2 < 90: Low oxygen saturation

  **Scoring:**
  - 0 rules matched: LOW risk (score <= 0.3)
  - 1-2 rules matched: MEDIUM risk (score 0.4-0.7)
  - 3+ rules matched: HIGH risk (score >= 0.8)

  When multiple records are provided, returns the highest risk assessment.
  ```
- responses:
  - 401: {"model": ErrorResponse, "description": "Invalid or missing Bearer token"}
  - 422: {"description": "Validation error (e.g., empty records list)"}

---

## Implementation Patterns

### Pydantic Field with Description
```python
from pydantic import Field

patient_id: str = Field(
    ...,
    description="Hospital patient identifier",
    examples=["P00001234"]
)
```

### Router Endpoint with Responses
```python
from app.presentation.schemas.error_schema import ErrorResponse

@router.post(
    "",
    response_model=PatientResponse,
    status_code=201,
    summary="Register a new patient",
    description="Creates a new patient record in the hospital system.",
    responses={
        401: {"model": ErrorResponse, "description": "Invalid or missing Bearer token"},
        409: {"model": ErrorResponse, "description": "Patient ID already exists"},
    }
)
async def register_patient(...):
    ...
```

### Path/Query Parameter with Description
```python
from fastapi import Path, Query

patient_id: str = Path(
    ...,
    description="Hospital patient identifier",
    examples=["P00001234"]
)

from_: datetime = Query(
    ...,
    alias="from",
    description="Start of time range, inclusive (ISO 8601 format)",
    examples=["2025-12-01T00:00:00Z"]
)
```

---

## Verification Checklist

### Task 1: Foundation
- [ ] `error_schema.py` created with ErrorResponse model
- [ ] `main.py` updated with `openapi_tags`

### Task 2: Patient
- [ ] `PatientCreateRequest` fields have descriptions and examples
- [ ] `PatientUpdateRequest` fields have descriptions and examples
- [ ] `PatientResponse` has complete field docs with model example
- [ ] `register_patient` endpoint has summary, description, responses (401, 409)
- [ ] `update_patient` endpoint has summary, description, path param, responses (401, 404, 409)

### Task 3: Vital
- [ ] `VitalCreateRequest` fields documented with units
- [ ] `VitalUpdateRequest` fields documented
- [ ] `VitalResponse`, `VitalItem`, `VitalListResponse` documented
- [ ] `create_vital` endpoint documented with responses (401, 404)
- [ ] `get_vitals` endpoint documented with path/query params, responses (401)
- [ ] `update_vital` endpoint documented with path param, responses (401, 404, 409)

### Task 4: Inference
- [ ] `VitalRecord` fields documented
- [ ] `InferenceRequest` fields documented
- [ ] `InferenceResponse` fields documented with complete example
- [ ] `evaluate_vital_risk` endpoint documented with risk rules, responses (401, 422)

### Final Verification
- [ ] Start app: `uvicorn app.main:app --reload`
- [ ] Swagger UI (`/docs`) shows all documentation
- [ ] All endpoints show lock icon (security requirement)
- [ ] Error responses visible per endpoint
- [ ] ReDoc (`/redoc`) renders properly
- [ ] `openapi.json` contains security scheme and all descriptions
