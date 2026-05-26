from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.user import UserResponse


IPB_STUDENT_DOMAIN = "@apps.ipb.ac.id"


class _MahasiswaBase(BaseModel):
    nama: str = Field(min_length=2, max_length=150)
    nim: str = Field(min_length=11, max_length=11, description="NIM IPB format: 1 huruf + 10 angka, contoh: G6401231033")
    fakultas: str = Field(min_length=2, max_length=100)
    program_studi: str = Field(min_length=2, max_length=100)
    semester: int = Field(default=1, ge=1, le=14)


class MahasiswaRegister(_MahasiswaBase):
    """Payload untuk register mahasiswa (gabungan user + mahasiswa)."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=30, description="Password 8-30 karakter: huruf, angka, atau simbol")

    @field_validator("email", mode="before")
    @classmethod
    def email_to_lowercase(cls, v: str) -> str:
        """Ensure email selalu lowercase."""
        if isinstance(v, str):
            return v.lower()
        return v

    @field_validator("email")
    @classmethod
    def email_harus_apps_ipb(cls, v: str) -> str:
        if not v.endswith(IPB_STUDENT_DOMAIN):
            raise ValueError(f"Email mahasiswa harus menggunakan domain {IPB_STUDENT_DOMAIN}")
        return v

    @field_validator("nim")
    @classmethod
    def nim_format_ipb(cls, v: str) -> str:
        """Validasi NIM IPB: 1 huruf + 10 angka."""
        v = v.upper()
        if len(v) != 11:
            raise ValueError("NIM IPB harus 11 karakter (1 huruf + 10 angka)")
        if not v[0].isalpha():
            raise ValueError("Karakter pertama NIM harus huruf")
        if not v[1:].isdigit():
            raise ValueError("10 karakter terakhir NIM harus angka")
        return v


class MahasiswaUpdate(BaseModel):
    nama: str | None = Field(default=None, min_length=2, max_length=150)
    fakultas: str | None = Field(default=None, min_length=2, max_length=100)
    program_studi: str | None = Field(default=None, min_length=2, max_length=100)
    semester: int | None = Field(default=None, ge=1, le=14)
    foto_profile: str | None = Field(default=None, max_length=255)


class MahasiswaResponse(UserResponse):
    model_config = ConfigDict(from_attributes=True)

    mahasiswa_id: int
    nim: str
    fakultas: str
    program_studi: str
    semester: int
    foto_profile: str | None = Field(default=None, max_length=255)


class MahasiswaDetailResponse(MahasiswaResponse):
    """Response lengkap dengan data user (untuk /me endpoint)."""
    user: UserResponse
