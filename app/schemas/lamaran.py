from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.domain.lamaran import StatusLamaran
from app.schemas.kegiatan import KegiatanListResponse
from app.schemas.mahasiswa import MahasiswaResponse


class LamaranCreate(BaseModel):
    mbkm_id: int = Field(gt=0)
    berkas_pendaftaran: str = Field(min_length=1, max_length=255, description="Path/URL berkas")


class LamaranStatusUpdate(BaseModel):
    status_pendaftaran: StatusLamaran


class LamaranResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    lamaran_id: int
    mahasiswa_id: int
    mbkm_id: int
    berkas_pendaftaran: str
    tanggal_daftar: date
    status_pendaftaran: StatusLamaran


class LamaranDetailResponse(LamaranResponse):
    """Response dengan data mahasiswa dan kegiatan (untuk detail view)."""
    mahasiswa: MahasiswaResponse
    kegiatan: KegiatanListResponse