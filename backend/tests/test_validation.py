import pytest
from pydantic import ValidationError

from app.api.user import VelogUsernameRequest


class TestVelogUsernameValidation:
    """Velog 사용자명 유효성 검사 테스트"""

    def test_valid_username(self):
        """정상적인 사용자명"""
        request = VelogUsernameRequest(username="testuser")
        assert request.username == "testuser"

    def test_username_with_at_sign(self):
        """@ 기호가 포함된 사용자명"""
        request = VelogUsernameRequest(username="@testuser")
        assert request.username == "testuser"

    def test_username_with_underscore(self):
        """언더스코어가 포함된 사용자명"""
        request = VelogUsernameRequest(username="test_user")
        assert request.username == "test_user"

    def test_username_with_hyphen(self):
        """하이픈이 포함된 사용자명"""
        request = VelogUsernameRequest(username="test-user")
        assert request.username == "test-user"

    def test_username_with_numbers(self):
        """숫자가 포함된 사용자명"""
        request = VelogUsernameRequest(username="user123")
        assert request.username == "user123"

    def test_empty_username(self):
        """빈 사용자명"""
        with pytest.raises(ValidationError):
            VelogUsernameRequest(username="")

    def test_whitespace_only_username(self):
        """공백만 있는 사용자명"""
        with pytest.raises(ValidationError):
            VelogUsernameRequest(username="   ")

    def test_username_too_long(self):
        """너무 긴 사용자명"""
        with pytest.raises(ValidationError):
            VelogUsernameRequest(username="a" * 51)

    def test_username_with_special_chars(self):
        """특수문자가 포함된 사용자명"""
        with pytest.raises(ValidationError):
            VelogUsernameRequest(username="user@name!")

    def test_username_with_korean(self):
        """한글이 포함된 사용자명"""
        with pytest.raises(ValidationError):
            VelogUsernameRequest(username="사용자명")

    def test_username_with_spaces(self):
        """공백이 포함된 사용자명"""
        with pytest.raises(ValidationError):
            VelogUsernameRequest(username="test user")
