# aitrics_assignment
aitrics 비대면 과제.

# Assume
1. vital 교정 API의 request 에 없는 값이 있어 이를 추가함.
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
   
2. Inference API 의 input 이 list type 인데 여러 값이 들어온 경우에 대한 처리 규칙이 없어 최대 위험도를 사용함.
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
   
# Modifications
- Auth token
과제에서 Auth token 을 단순 환경변수로 설정해 이를 검증하도록 요구함. 그러나 이는 보안 레벨이 너무 낮아 JWT 기반으로 구현함.
    - doctor model 추가: API 를 사용할 수 있음.
    - `/auth/register` API 신설: doctor 추가. ID, password, name, email, phone 을 받음.
    - `/auth/login` API 신설: 1시간동안 사용할 수 있는 access token 과 refresh token을 발급.
    - `/auth/refresh-token` API 신설 : refresh token 을 이용해 새 access token 을 발급
    - JWT token: 다음 값을 access_token 으로 encode 해 Bearer header로 전송.
    ```json5
    {
      "iat": "{current_timestamp}",
      "exp": "{current_timestamp + 3min}",
      "iss": "{doctor.id}",
      "aud": "aitrics",
    }
    ```
    - Token 검증: 다음 중 하나라도 해당되면 요청 거절
        - access_token 이 일치하지 않음 (signature 불일치)
        - access_token 이 expire 되었음
        - access_token 소유자와 token내의 iss가 일치하지 않음
        - iat 가 현재보다 3분 이상 미래임
        - exp 가 과거임
  
# How to use
