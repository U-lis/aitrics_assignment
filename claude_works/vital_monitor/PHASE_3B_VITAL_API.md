# Phase 3B: Vital Data API

## Objective

Implement vital data CRUD with optimistic locking.

**Note:** This phase can run in parallel with Phase 3A and 3C.

## APIs

- `POST /api/v1/vitals` - Save vital data
- `GET /api/v1/patients/{patient_id}/vitals` - Query by time range
- `PUT /api/v1/vitals/{vital_id}` - Update with version check (Optimistic Lock)

## Tasks

### 1. Create Vital Schemas

Location: `src/app/presentation/schemas/vital_schema.py`

```python
class VitalCreateRequest(BaseModel):
    patient_id: str
    recorded_at: datetime
    vital_type: VitalType  # HR, RR, SBP, DBP, SpO2, BT
    value: float

class VitalUpdateRequest(BaseModel):
    value: float
    vital_type: VitalType  # Can change vital type
    version: int  # Required for optimistic lock

class VitalResponse(BaseModel):
    id: UUID
    patient_id: str
    recorded_at: datetime
    vital_type: str
    value: float
    version: int
    created_at: datetime
    updated_at: datetime

class VitalItem(BaseModel):
    recorded_at: datetime
    value: float

class VitalListResponse(BaseModel):
    patient_id: str
    vital_type: str | None
    items: list[VitalItem]
```

### 2. Create VitalService

Location: `src/app/application/vital_service.py`

**create_vital(dto):**
- Validate patient exists
- Validate vital_type is valid enum
- Create vital record

**get_vitals(patient_id, from_, to, vital_type=None):**
```python
query = select(VitalModel).where(
    VitalModel.patient_id == patient_id,
    VitalModel.recorded_at >= from_,
    VitalModel.recorded_at <= to
)
if vital_type:
    query = query.where(VitalModel.vital_type == vital_type)

query = query.order_by(VitalModel.recorded_at)
return await session.scalars(query)
```

**update_vital(vital_id, dto):**
```python
# Use optimistic locking pattern
stmt = update(VitalModel).where(
    VitalModel.id == vital_id,
    VitalModel.version == dto.version
).values(
    value=dto.value,
    vital_type=dto.vital_type,
    version=VitalModel.version + 1
).returning(VitalModel)

result = await session.execute(stmt)
updated = result.scalar_one_or_none()

if updated is None:
    existing = await repo.find_by_id(vital_id)
    if existing is None:
        raise VitalNotFoundError(vital_id)
    raise OptimisticLockError(f"Version mismatch")

return VitalResponse.from_orm(updated)
```

### 3. Create Vital Router

Location: `src/app/presentation/vital_router.py`

```python
router = APIRouter(tags=["vitals"])

@router.post("/api/v1/vitals", response_model=VitalResponse, status_code=201)
async def save_vital(
    request: VitalCreateRequest,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db_session)
):
    ...

@router.get("/api/v1/patients/{patient_id}/vitals", response_model=VitalListResponse)
async def get_vitals(
    patient_id: str,
    from_: datetime = Query(..., alias="from"),
    to: datetime = Query(...),
    vital_type: VitalType | None = None,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db_session)
):
    ...

@router.put("/api/v1/vitals/{vital_id}", response_model=VitalResponse)
async def update_vital(
    vital_id: UUID,
    request: VitalUpdateRequest,
    doctor: Doctor = Depends(get_current_doctor),
    db: AsyncSession = Depends(get_db_session)
):
    ...
```

### 4. Register Exception Handlers

- VitalNotFoundError -> 404 Not Found
- PatientNotFoundError -> 404 Not Found (on create)
- OptimisticLockError -> 409 Conflict

## Checklist

- [x] Vital schemas created (with vital_type in update)
- [x] VitalService created
- [x] Vital router created
- [x] Patient validation on vital create
- [x] Time range query implemented
- [x] Optional vital_type filter
- [x] Auth dependency applied to all routes
- [x] 409 Conflict on version mismatch

## Test Cases

### Vital API E2E (tests/e2e/test_vital_api.py)

| Test | Description |
|------|-------------|
| test_create_vital_success | POST /api/v1/vitals → 201 |
| test_create_vital_invalid_patient | Unknown patient_id → 404 |
| test_create_vital_invalid_type | Invalid vital_type → 422 |
| test_create_vital_unauthorized | No token → 401 |
| test_get_vitals_success | GET /api/v1/patients/{id}/vitals → 200 |
| test_get_vitals_time_range | from/to filter works |
| test_get_vitals_type_filter | vital_type filter works |
| test_get_vitals_empty | No data in range → empty array |
| test_get_vitals_unauthorized | No token → 401 |
| test_update_vital_success | PUT /api/v1/vitals/{id} → 200 |
| test_update_vital_change_type | Can change vital_type |
| test_update_vital_optimistic_lock_conflict | Version mismatch → 409 |
| test_update_vital_not_found | Unknown vital_id → 404 |
