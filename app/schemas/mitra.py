from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.user import UserResponse


_BLOCKED_MITRA_DOMAINS = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com"}


class _MitraBase(BaseModel):
    nama_instansi: str = Field(min_length=2, max_length=200)
    jenis_instansi: str = Field(min_length=2, max_length=100)
    alamat: str = Field(min_length=5, max_length=255)
    kontak: str = Field(min_length=5, max_length=50)


class MitraRegister(_MitraBase):
    """Payload register mitra (gabungan user + mitra)."""
    nama: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=8, max_length=10, description="Password 8-10 karakter: huruf, angka, atau simbol")

    @field_validator("email", mode="before")
    @classmethod
    def email_to_lowercase(cls, v: str) -> str:
        """Ensure email selalu lowercase."""
        if isinstance(v, str):
            return v.lower()
        return v

    @field_validator("email")
    @classmethod
    def email_harus_perusahaan(cls, v: str) -> str:
        domain = v.split("@", 1)[-1]
        if domain in _BLOCKED_MITRA_DOMAINS:
            raise ValueError(
                "Mitra harus menggunakan email perusahaan (bukan email personal)"
            )
        return v


class MitraUpdate(BaseModel):
    nama_instansi: str | None = Field(default=None, min_length=2, max_length=200)
    jenis_instansi: str | None = Field(default=None, min_length=2, max_length=100)
    alamat: str | None = Field(default=None, min_length=5, max_length=255)
    kontak: str | None = Field(default=None, min_length=5, max_length=50)


class MitraResponse(UserResponse):
    model_config = ConfigDict(from_attributes=True)

    mitra_id: int
    nama_instansi: str
    jenis_instansi: str
    alamat: str
    kontak: str


class MitraDetailResponse(MitraResponse):
    user: UserResponse
