"""
Domain entity: User.
Cuman logic bisnis.
"""
import enum
from dataclasses import dataclass
from datetime import datetime


class UserRole(str, enum.Enum):
    MAHASISWA = "mahasiswa"
    MITRA = "mitra"


@dataclass
class User:
    """Domain entity untuk user (account)."""
    nama: str
    email: str
    password_hash: str
    role: UserRole
    user_id: int | None = None
    created_at: datetime | None = None

    @property
    def password(self) -> str:
        """Alias class diagram; nilai sebenarnya tetap password hash."""
        return self.password_hash

    @password.setter
    def password(self, password_hash: str) -> None:
        self.password_hash = password_hash

    def login(self, email: str, password: str) -> bool:
        """Cek kredensial pada level entity.

        Verifikasi password plaintext tetap dilakukan di app.security.
        """
        return self.email == email.lower() and self.password_hash == password

    def logout(self) -> None:
        """JWT bersifat stateless, jadi logout tidak mengubah state entity."""
        return None

    def update_profil(
        self,
        nama: str | None = None,
        email: str | None = None,
    ) -> None:
        if nama is not None:
            self.nama = nama
        if email is not None:
            self.email = email.lower()

    def ganti_password(self, password_hash_baru: str) -> None:
        """Ganti password (hashnya, bukan plaintext)."""
        self.password_hash = password_hash_baru

    def is_mahasiswa(self) -> bool:
        return self.role == UserRole.MAHASISWA

    def is_mitra(self) -> bool:
        return self.role == UserRole.MITRA
