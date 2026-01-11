import pytest
from fastapi import HTTPException

from app.dependencies import verify_bearer_token


class TestVerifyBearerToken:
    def test_valid_token(self, monkeypatch):
        """Valid token should return True."""
        monkeypatch.setenv("BEARER_TOKEN", "test-token-123")

        # Clear settings cache
        from app.config import get_settings

        get_settings.cache_clear()

        # Create mock credentials
        class MockCredentials:
            credentials = "test-token-123"

        result = verify_bearer_token(MockCredentials())  # ty: ignore[invalid-argument-type]
        assert result is True

    def test_invalid_token_raises_401(self, monkeypatch):
        """Invalid token should raise HTTPException with 401."""
        monkeypatch.setenv("BEARER_TOKEN", "correct-token")

        from app.config import get_settings

        get_settings.cache_clear()

        class MockCredentials:
            credentials = "wrong-token"

        with pytest.raises(HTTPException) as exc_info:
            verify_bearer_token(MockCredentials())  # ty: ignore[invalid-argument-type]

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid token"
        assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}

    def test_empty_token_raises_401(self, monkeypatch):
        """Empty token should raise HTTPException with 401."""
        monkeypatch.setenv("BEARER_TOKEN", "valid-token")

        from app.config import get_settings

        get_settings.cache_clear()

        class MockCredentials:
            credentials = ""

        with pytest.raises(HTTPException) as exc_info:
            verify_bearer_token(MockCredentials())  # ty: ignore[invalid-argument-type]

        assert exc_info.value.status_code == 401
