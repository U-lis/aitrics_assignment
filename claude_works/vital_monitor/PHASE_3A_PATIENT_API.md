# Phase 3A: Patient API

## Objective

Implement patient registration and update with optimistic locking.

**Note:** This phase can run in parallel with Phase 3B and 3C.

## APIs

- `POST /api/v1/patients` - Register patient
- `PUT /api/v1/patients/{patient_id}` - Update with version check (Optimistic Lock)

## Tasks

### 1. Create Patient Schemas

Location: `src/app/presentation/schemas/patient_schema.py`

```python
class PatientCreateRequest(BaseModel):
    patient_id: str  # e.g., "P00001234"
    name: str
    gender: Literal["M", "F"]
    birth_date: date

class PatientUpdateRequest(BaseModel):
    name: str
    gender: Literal["M", "F"]
    birth_date: date
    version: int  # Required for optimistic lock

class PatientResponse(BaseModel):
    id: UUID
    patient_id: str
    name: str
    gender: str
    birth_date: date
    version: int
    created_at: datetime
    updated_at: datetime
```

### 2. Create PatientService

Location: `src/app/application/patient_service.py`

**create_patient(dto):**
- Check if patient_id already exists
- Create patient record
- Return PatientResponse

**update_patient(patient_id, dto):**
```python
# Use optimistic locking pattern
stmt = update(PatientModel).where(
    PatientModel.patient_id == patient_id,
    PatientModel.version == dto.version
).values(
    name=dto.name,
    gender=dto.gender,
    birth_date=dto.birth_date,
    version=PatientModel.version + 1
).returning(PatientModel)

result = await session.execute(stmt)
updated = result.scalar_one_or_none()

if updated is None:
    existing = await repo.find_by_patient_id(patient_id)
    if existing is None:
        raise PatientNotFoundError(patient_id)
    raise OptimisticLockError(f"Version mismatch: expected {dto.version}, current {existing.version}")

return PatientResponse.from_orm(updated)
```

### 3. Create Patient Router

Location: `src/app/presentation/patient_router.py`

```python
router = APIRouter(prefix="/api/v1/patients", tags=["patients"])

@router.post("", response_model=PatientResponse, status_code=201)
async def register_patient(
    request: PatientCreateRequest,
    doctor: Doctor = Depends(get_current_doctor),  # Auth required
    db: AsyncSession = Depends(get_db_session)
):
    ...

@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: str,
    request: PatientUpdateRequest,
    doctor: Doctor = Depends(get_current_doctor),  # Auth required
    db: AsyncSession = Depends(get_db_session)
):
    ...
```

### 4. Register Exception Handlers

In `main.py`:
- OptimisticLockError -> 409 Conflict
- PatientNotFoundError -> 404 Not Found

## Checklist

- [ ] Patient schemas created
- [ ] PatientService with optimistic lock created
- [ ] Patient router created
- [ ] Auth dependency applied to all routes
- [ ] Exception handlers registered
- [ ] 409 Conflict on version mismatch
- [ ] 404 Not Found on missing patient

## Test Cases (TBD)

To be discussed with user.
