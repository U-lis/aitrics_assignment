# **1. 도메인 설명 – Vital 데이터란?**

병원에서는 환자의 상태 변화를 모니터링하기 위해 다양한 **Vital Signs**(생체징후) 데이터를 실시간 수집합니다.

본 과제에서는 아래 6개의 Vital 유형을 사용합니다.

| Vital Type | 설명 | 단위 |
| --- | --- | --- |
| HR | 심박수 (Heart Rate) | bpm |
| RR | 호흡수 (Respiratory Rate) | breaths/min |
| SBP | 수축기 혈압 | mmHg |
| DBP | 이완기 혈압 | mmHg |
| SpO2 | 산소포화도 | % |
| BT | 체온 | ℃ |

Vital 데이터는 시간에 따라 수집되는 **시계열(Time-series) 데이터**이며, 의료 AI 모델의 입력으로 사용됩니다.

---

# **2. 기능 요구사항**

아래 API 및 기능을 구현해야 합니다.

---

## **2-1. 환자 관리 API**

### **(1) 환자 등록 API**

- **Method**: `POST`
- **Endpoint**: `/api/v1/patients`

**Request 예시**

```
{
  "patient_id": "P00001234",
  "name": "홍길동",
  "gender": "M",
  "birth_date": "1975-03-01"
}

```

---

### **(2) 환자 정보 수정 API (Optimistic Lock 必 적용)**

> ⚠ 반드시 요청과 DB의 version 비교를 통한 낙관적 락 적용
> 
- **Method**: `PUT`
- **Endpoint**: `/api/v1/patients/{patient_id}`

**제약사항**

- Request Body에 `version` 필수
- DB version과 다르면 → `409 Conflict` 반환

**Request 예시**

```
{
  "name": "홍길동",
  "gender": "M",
  "birth_date": "1975-03-01",
  "version": 3
}

```

---

## **2-2. Vital 데이터 API**

### **(1) Vital 데이터 저장 API**

- **Method**: `POST`
- **Endpoint**: `/api/v1/vitals`

**Request 예시**

```
{
  "patient_id": "P00001234",
  "recorded_at": "2025-12-01T10:15:00Z",
  "vital_type": "HR",
  "value": 110.0
}

```

**제약**

- 등록된 환자만 입력 가능
- vital_type ∈ `["HR", "RR", "SBP", "DBP", "SpO2", "BT"]`

---

### **(2) Vital 데이터 조회 API**

- **Method**: `GET`
- **Endpoint**: `/api/v1/patients/{patient_id}/vitals`

**Query Parameters**

- `from` (필수)
- `to` (필수)
- `vital_type` (선택)

**Response 예시**

```
{
  "patient_id": "P00001234",
  "vital_type": "HR",
  "items": [
    {
      "recorded_at": "2025-12-01T10:15:00Z",
      "value": 110.0
    }
  ]
}

```

---

### **(3) Vital 데이터 교정 API (Optimistic Lock 必 적용)**

- **Method**: `PUT`
- **Endpoint**: `/api/v1/vitals/{vital_id}`

**요구사항**

- Request Body에 `version` 필수
- version mismatch → `409 Conflict`

**Request 예시**

```
{
  "value": 115.0,
  "version": 2
}

```

---

## **2-3. Inference API (단순 Rule 기반 위험 스코어)**

### **(1) Inference 요청 API**

- **Method**: `POST`
- **Endpoint**: `/api/v1/inference/vital-risk`

**Request 예시**

```
{
  "patient_id": "P00001234",
  "records": [
    {
      "recorded_at": "2025-12-01T10:15:00Z",
      "vitals": {
        "HR": 130.0,
        "SBP": 85.0,
        "SpO2": 89.0
      }
    }
  ]
}

```

### **평가 규칙**

| 조건 | 의미 |
| --- | --- |
| HR > 120 | 위험 증가 |
| SBP < 90 | 위험 증가 |
| SpO2 < 90 | 위험 증가 |

충족 개수에 따른 risk score:

| 충족 개수 | risk_score | risk_level |
| --- | --- | --- |
| 0 | ≤0.3 | LOW |
| 1–2 | 0.4–0.7 | MEDIUM |
| ≥3 | ≥0.8 | HIGH |

**Response 예시**

```
{
  "patient_id": "P00001234",
  "risk_score": 0.91,
  "risk_level": "HIGH",
  "checked_rules": ["HR > 120", "SBP < 90", "SpO2 < 90"],
  "evaluated_at": "2025-12-01T10:20:00Z"
}

```

---

# **3. 인증 요구사항**

- 모든 API는 **Bearer Token 기반 인증** 적용
- 인증 실패 시 → `401 Unauthorized`

**Header 예시**

```
Authorization: Bearer <token>

```

- 토큰은 환경 변수 또는 설정 파일로 관리

---

# **4. 비기능 요구사항**

| 항목 | 설명 |
| --- | --- |
| 아키텍처 | Layered 또는 DDD-lite 구조 권장 |
| 테스트 | 높은 유닛 테스트 커버리지 |
| Dockerfile | 로컬 실행 가능하도록 제공 |
| Swagger/OpenAPI | API 문서 포함 |
| Config | 환경파일(.env 등)로 분리하여 온프레미스 대응 |

---

# **5. Optimistic Lock 필수 적용 지점 (2곳)**

다음 두 API는 **반드시 version 기반 낙관적 락 적용이 필수입니다.**

## **(A) 환자 수정 API**

`PUT /patients/{id}`

- version mismatch → `409 Conflict`

## **(B) Vital 교정 API**

`PUT /vitals/{vital_id}`

- version mismatch → `409 Conflict`

---

# **6. 제출물 안내**

제출물은 GitHub Repo 또는 ZIP 형태로 제출합니다.

필수 포함 항목:

- README
- 실행 방법
- Swagger/OpenAPI 명세 (URL 또는 파일)
- DB 스키마 (DDL 포함 가능)
- Optimistic Lock 설계 및 동작 설명
- Claude/ChatGPT 활용 기록
    - 예: `claude.md`, `chatgpt.md`
    - 사용한 Prompt, 채택한 아이디어, 미채택 이유 등 명시

---

# **7. 과제 난이도 & 조언**

본 과제는 **3–6시간 정도 분량**을 목표로 설계되었으며, 개발 언어는 자율입니다.

불필요한 복잡도보다 **설계의 명확성 / 품질 / 동시성 처리 이해도**를 중점적으로 평가합니다.