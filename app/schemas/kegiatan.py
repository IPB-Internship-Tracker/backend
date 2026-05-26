from datetime import date

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator

from app.domain.kegiatan import (
    BidangMagang,
    DokumenLamaran,
    KategoriMBKM,
    PenempatanMagang,
    StatusKegiatan,
    TipeGaji,
)


class _KegiatanCommonBase(BaseModel):
    nama_kegiatan: str = Field(min_length=3, max_length=200)
    deskripsi: str = Field(min_length=10)
    deadline_pendaftaran: date
    tanggal_mulai: date
    tanggal_selesai: date

    @model_validator(mode="after")
    def validasi_tanggal(self) -> "_KegiatanCommonBase":
        if self.tanggal_selesai < self.tanggal_mulai:
            raise ValueError("tanggal_selesai tidak boleh sebelum tanggal_mulai")
        if self.deadline_pendaftaran > self.tanggal_mulai:
            raise ValueError("deadline_pendaftaran tidak boleh setelah tanggal_mulai")
        return self


class _KegiatanBase(_KegiatanCommonBase):
    narahubung: str = Field(min_length=2, max_length=150)
    kuota: int = Field(gt=0, le=10000)
    syarat_ketentuan: str = Field(min_length=5)
    info_lebih_lanjut: str = Field(min_length=2)


class _KegiatanCommonUpdateBase(BaseModel):
    nama_kegiatan: str | None = Field(default=None, min_length=3, max_length=200)
    deskripsi: str | None = Field(default=None, min_length=10)
    deadline_pendaftaran: date | None = None
    status: StatusKegiatan | None = None
    tanggal_mulai: date | None = None
    tanggal_selesai: date | None = None


class _KegiatanUpdateBase(_KegiatanCommonUpdateBase):
    narahubung: str | None = Field(default=None, min_length=2, max_length=150)
    kuota: int | None = Field(default=None, gt=0, le=10000)
    syarat_ketentuan: str | None = Field(default=None, min_length=5)
    info_lebih_lanjut: str | None = Field(default=None, min_length=2)


class _KegiatanCommonResponseBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    mbkm_id: int
    mitra_id: int
    nama_kegiatan: str
    deskripsi: str
    kategori_mbkm: KategoriMBKM
    deadline_pendaftaran: date
    status: StatusKegiatan
    tanggal_mulai: date
    tanggal_selesai: date


class _KegiatanResponseBase(_KegiatanCommonResponseBase):
    narahubung: str
    kuota: int
    syarat_ketentuan: str
    info_lebih_lanjut: str


# ---------- Magang ----------
class MagangCreate(_KegiatanBase):
    bidang: BidangMagang
    posisi: str = Field(min_length=2, max_length=100)
    nama_perusahaan: str | None = Field(default=None, min_length=2, max_length=200)
    logo_url: str | None = Field(default=None, max_length=255)
    penempatan: PenempatanMagang = PenempatanMagang.WFO
    kota_lokasi: str = Field(
        validation_alias=AliasChoices("kota_lokasi", "lokasi"),
        min_length=2,
        max_length=150,
    )
    alamat_lengkap: str = Field(min_length=5, max_length=255)
    tipe_gaji: TipeGaji = TipeGaji.UNPAID
    gaji_perbulan: float = Field(
        default=0.0,
        ge=0,
        validation_alias=AliasChoices("gaji_perbulan", "uang_saku"),
    )
    dokumen_dibutuhkan: list[DokumenLamaran] = Field(min_length=1)


class MagangUpdate(_KegiatanUpdateBase):
    bidang: BidangMagang | None = None
    posisi: str | None = Field(default=None, min_length=2, max_length=100)
    nama_perusahaan: str | None = Field(default=None, min_length=2, max_length=200)
    logo_url: str | None = Field(default=None, max_length=255)
    penempatan: PenempatanMagang | None = None
    kota_lokasi: str | None = Field(
        default=None,
        validation_alias=AliasChoices("kota_lokasi", "lokasi"),
        min_length=2,
        max_length=150,
    )
    alamat_lengkap: str | None = Field(default=None, min_length=5, max_length=255)
    tipe_gaji: TipeGaji | None = None
    gaji_perbulan: float | None = Field(
        default=None,
        ge=0,
        validation_alias=AliasChoices("gaji_perbulan", "uang_saku"),
    )
    dokumen_dibutuhkan: list[DokumenLamaran] | None = Field(default=None, min_length=1)


class MagangResponse(_KegiatanResponseBase):
    bidang: BidangMagang
    posisi: str
    nama_perusahaan: str
    logo_url: str | None
    penempatan: PenempatanMagang
    kota_lokasi: str
    alamat_lengkap: str
    tipe_gaji: TipeGaji
    gaji_perbulan: float
    dokumen_dibutuhkan: list[DokumenLamaran]


# ---------- Lomba ----------
class _LombaStudiBase(BaseModel):
    nama_kegiatan: str = Field(min_length=3, max_length=200)
    poster: str = Field(min_length=1, max_length=255)
    deskripsi: str = Field(min_length=10)
    deadline_pendaftaran: date
    tanggal_mulai: date
    tanggal_selesai: date
    bidang: str = Field(min_length=2, max_length=100)

    @model_validator(mode="after")
    def validasi_tanggal(self) -> "_LombaStudiBase":
        if self.tanggal_selesai < self.tanggal_mulai:
            raise ValueError("tanggal_selesai tidak boleh sebelum tanggal_mulai")
        if self.deadline_pendaftaran > self.tanggal_mulai:
            raise ValueError("deadline_pendaftaran tidak boleh setelah tanggal_mulai")
        return self


class _LombaStudiUpdateBase(BaseModel):
    nama_kegiatan: str | None = Field(default=None, min_length=3, max_length=200)
    poster: str | None = Field(default=None, min_length=1, max_length=255)
    deskripsi: str | None = Field(default=None, min_length=10)
    deadline_pendaftaran: date | None = None
    status: StatusKegiatan | None = None
    tanggal_mulai: date | None = None
    tanggal_selesai: date | None = None
    bidang: str | None = Field(default=None, min_length=2, max_length=100)


class _LombaStudiResponseBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    mbkm_id: int
    mitra_id: int
    nama_kegiatan: str
    poster: str
    deskripsi: str
    kategori_mbkm: KategoriMBKM
    deadline_pendaftaran: date
    status: StatusKegiatan
    tanggal_mulai: date
    tanggal_selesai: date
    bidang: str


class LombaCreate(_LombaStudiBase):
    pass


class LombaUpdate(_LombaStudiUpdateBase):
    pass


class LombaResponse(_LombaStudiResponseBase):
    pass


# ---------- Studi Independen ----------
class StudiIndependenCreate(_LombaStudiBase):
    pass


class StudiIndependenUpdate(_LombaStudiUpdateBase):
    pass


class StudiIndependenResponse(_LombaStudiResponseBase):
    pass


# ---------- Polymorphic list response ----------
class KegiatanListResponse(_KegiatanResponseBase):
    """Ringkas untuk endpoint list dengan field utama Magang jika tersedia."""

    bidang: BidangMagang | str | None = None
    posisi: str | None = None
    nama_perusahaan: str | None = None
    logo_url: str | None = None
    poster: str | None = None
    penempatan: PenempatanMagang | None = None
    kota_lokasi: str | None = None
    alamat_lengkap: str | None = None
    tipe_gaji: TipeGaji | None = None
    gaji_perbulan: float | None = None
    dokumen_dibutuhkan: list[DokumenLamaran | str] | None = None


KegiatanResponse = (
    MagangResponse | LombaResponse | StudiIndependenResponse
)
