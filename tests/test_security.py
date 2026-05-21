"""
Unit test untuk security (password hashing + JWT).
"""
from datetime import timedelta

import pytest

from app.domain.user import UserRole
from app.security import (
    create_access_token,
    create_password_reset_token,
    decode_access_token,
    decode_password_reset_token,
    hash_password,
    verify_password,
)


class TestPasswordHash:
    def test_hash_tidak_sama_dengan_password(self):
        h = hash_password("rahasia123")
        assert h != "rahasia123"
        assert len(h) > 50  # bcrypt hash ~60 char

    def test_verify_password_benar(self):
        h = hash_password("rahasia123")
        assert verify_password("rahasia123", h) is True

    def test_verify_password_salah(self):
        h = hash_password("rahasia123")
        assert verify_password("salah", h) is False

    def test_hash_sama_password_beda_output(self):
        """bcrypt menambah salt random, jadi hash selalu beda untuk password yang sama."""
        h1 = hash_password("rahasia123")
        h2 = hash_password("rahasia123")
        assert h1 != h2
        # Tapi keduanya valid untuk password yang sama
        assert verify_password("rahasia123", h1)
        assert verify_password("rahasia123", h2)


class TestJWT:
    def test_create_dan_decode(self):
        token = create_access_token(user_id=42, role=UserRole.MAHASISWA)
        payload = decode_access_token(token)
        assert payload["sub"] == "42"
        assert payload["role"] == "mahasiswa"
        assert "exp" in payload

    def test_token_berbeda_role(self):
        t_mhs = create_access_token(user_id=1, role=UserRole.MAHASISWA)
        t_mitra = create_access_token(user_id=1, role=UserRole.MITRA)
        assert decode_access_token(t_mhs)["role"] == "mahasiswa"
        assert decode_access_token(t_mitra)["role"] == "mitra"

    @pytest.mark.parametrize("token_rusak", [
        "bukan.token.valid",
        "abc",
        "",
        "eyJhbGciOiJIUzI1NiJ9.x.y",
    ])
    def test_token_invalid_ditolak(self, token_rusak):
        with pytest.raises(ValueError, match="Token tidak valid"):
            decode_access_token(token_rusak)

    def test_token_expired_ditolak(self):
        token = create_access_token(
            user_id=1, role=UserRole.MAHASISWA,
            expires_delta=timedelta(seconds=-1),
        )
        with pytest.raises(ValueError, match="Token tidak valid"):
            decode_access_token(token)

    def test_token_signature_dipalsukan_ditolak(self):
        token = create_access_token(user_id=1, role=UserRole.MAHASISWA)
        token_palsu = token + "XXX"  # ubah signature
        with pytest.raises(ValueError):
            decode_access_token(token_palsu)

    def test_password_reset_token(self):
        token = create_password_reset_token(user_id=7, role=UserRole.MITRA)
        payload = decode_password_reset_token(token)
        assert payload["sub"] == "7"
        assert payload["role"] == "mitra"
        assert payload["purpose"] == "password_reset"

    def test_access_token_tidak_bisa_dipakai_reset_password(self):
        token = create_access_token(user_id=7, role=UserRole.MITRA)
        with pytest.raises(ValueError, match="reset password"):
            decode_password_reset_token(token)
