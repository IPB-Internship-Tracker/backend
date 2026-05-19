from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.notifikasi import JenisNotifikasi


class NotifikasiCreate(BaseModel):
    user_id: int = Field(gt=0)
    judul: str = Field(min_length=1, max_length=200)
    pesan: str = Field(min_length=1)
    jenis_notifikasi: JenisNotifikasi


class NotifikasiResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    notifikasi_id: int
    user_id: int
    judul: str
    pesan: str
    jenis_notifikasi: JenisNotifikasi
    status_baca: bool
    created_at: datetime