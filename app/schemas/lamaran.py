from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.kegiatan import DokumenLamaran
from app.domain.lamaran import StatusLamaran
from app.schemas.kegiatan import KegiatanResponse
from app.schemas.mahasiswa import MahasiswaResponse


class LamaranCreate(BaseModel):
    mbkm_id: int = Field(gt=0)
    berkas_pendaftaran: dict[DokumenLamaran, str] = Field(
        min_length=1,
        description="Mapping dokumen wajib ke path/URL berkas",
    )

    @field_validator("berkas_pendaftaran")
    @classmethod
    def berkas_tidak_boleh_kosong(
        cls,
        value: dict[DokumenLamaran, str],
    ) -> dict[DokumenLamaran, str]:
        for dokumen, berkas in value.items():
            if not berkas or not berkas.strip():
                raise ValueError(f"Berkas untuk {dokumen.value} tidak boleh kosong")
            if len(berkas) > 255:
                raise ValueError(f"Path/URL berkas untuk {dokumen.value} maksimal 255 karakter")
        return value


class LamaranStatusUpdate(BaseModel):
    status_pendaftaran: StatusLamaran


class LamaranResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    lamaran_id: int
    mahasiswa_id: int
    mbkm_id: int
    berkas_pendaftaran: dict[DokumenLamaran | str, str]
    tanggal_daftar: date
    status_pendaftaran: StatusLamaran


class LamaranDetailResponse(LamaranResponse):
    """Response dengan data mahasiswa dan kegiatan (untuk detail view)."""
    mahasiswa: MahasiswaResponse
    kegiatan: KegiatanResponse
