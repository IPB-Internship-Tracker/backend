"""
Domain entity: User.
Cuman logic bisnis.
"""
import enum
from dataclasses import dataclass, field
from datetime import datetime


class UserRole(str, enum.Enum):
    MAHASISWA = "mahasiswa"
    MITRA = "mitra"
    ADMIN = "admin"


@dataclass
class User:
    """Domain entity untuk user (account)."""
    nama: str
    email: str
    password_hash: str
    role: UserRole
    user_id: int | None = None
    created_at: datetime | None = None

    def ganti_password(self, password_hash_baru: str) -> None:
        """Ganti password (hashnya, bukan plaintext)."""
        self.password_hash = password_hash_baru

    def is_mahasiswa(self) -> bool:
        return self.role == UserRole.MAHASISWA

    def is_mitra(self) -> bool:
        return self.role == UserRole.MITRA

    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN