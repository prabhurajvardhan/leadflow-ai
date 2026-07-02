import pytest
from datetime import datetime, timedelta
from app.core.security import (
    get_password_hash, verify_password,
    create_access_token, create_refresh_token, decode_token,
    verify_access_token, verify_refresh_token
)


class TestPasswordHashing:
    def test_password_hash_and_verify(self):
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed) is True
    
    def test_wrong_password_fails(self):
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False


class TestTokenCreation:
    def test_access_token_creation(self):
        data = {"sub": "123"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_access_token_with_expiry(self):
        data = {"sub": "123"}
        expires = timedelta(minutes=30)
        token = create_access_token(data, expires_delta=expires)
        
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "123"
        assert payload["type"] == "access"
    
    def test_refresh_token_creation(self):
        data = {"sub": "123"}
        token = create_refresh_token(data)
        
        assert token is not None
        payload = decode_token(token)
        assert payload["type"] == "refresh"


class TestTokenVerification:
    def test_verify_valid_access_token(self):
        data = {"sub": "123"}
        token = create_access_token(data)
        
        payload = verify_access_token(token)
        assert payload is not None
        assert payload["sub"] == "123"
    
    def test_verify_refresh_token_as_access_fails(self):
        data = {"sub": "123"}
        token = create_refresh_token(data)
        
        payload = verify_access_token(token)
        assert payload is None
    
    def test_verify_access_token_as_refresh_fails(self):
        data = {"sub": "123"}
        token = create_access_token(data)
        
        payload = verify_refresh_token(token)
        assert payload is None
    
    def test_verify_invalid_token(self):
        payload = verify_access_token("invalid_token")
        assert payload is None
