"""
Domain entity: KegiatanMBKM + subclass (Magang, Lomba, StudiIndependen).
Inheritance di level domain. Tidak ada SQLAlchemy.
"""
import enum
from dataclasses import dataclass, field
from datetime import date

from app.domain.exceptions import ForbiddenActionError


class KategoriMBKM(str, enum.Enum):
    MAGANG = "magang"
    LOMBA = "lomba"
    STUDI_INDEPENDEN = "studi_independen"


class StatusKegiatan(str, enum.Enum):
    DIBUKA = "dibuka"
    DITUTUP = "ditutup"
    BERLANGSUNG = "berlangsung"
    SELESAI = "selesai"


class BidangMagang(str, enum.Enum):
    INFORMATION_TECHNOLOGY = "Information Technology"
    DATA_ANALYTICS = "Data & Analytics"
    BUSINESS_MANAGEMENT = "Business & Management"
    MARKETING_COMMUNICATION = "Marketing & Communication"
    FINANCE_ACCOUNTING = "Finance & Accounting"
    HUMAN_RESOURCES = "Human Resources (HR)"
    OPERATIONS_LOGISTICS = "Operations & Logistics"
    ADMINISTRATION = "Administration"
    DESIGN_CREATIVE = "Design & Creative"
    ENGINEERING_NON_IT = "Engineering (Non-IT)"
    RESEARCH_DEVELOPMENT = "Research & Development"
    SALES_BUSINESS_DEVELOPMENT = "Sales & Business Development"
    LEGAL = "Legal"
    HEALTHCARE_LIFE_SCIENCES = "Healthcare / Life Sciences"


class PenempatanMagang(str, enum.Enum):
    HYBRID = "Hybrid"
    WFH = "WFH"
    WFO = "WFO"


class TipeGaji(str, enum.Enum):
    PAID = "Paid"
    UNPAID = "Unpaid"


class DokumenLamaran(str, enum.Enum):
    CV = "Curriculum Vitae (CV)"
    MOTIVATION_LETTER = "Motivation Letter"
    TRANSKRIP_NILAI = "Transkrip Nilai"
    SURAT_REKOMENDASI_KAMPUS = "Surat Rekomendasi Kampus"
    SURAT_IZIN_DOSEN_PEMBIMBING = "Surat Izin Dosen Pembimbing"
    PORTOFOLIO = "Portofolio"


@dataclass
class KegiatanMBKM:
    """Base class domain untuk semua kegiatan MBKM."""
    mitra_id: int
    nama_kegiatan: str
    deskripsi: str
    kategori_mbkm: KategoriMBKM
    deadline_pendaftaran: date
    kuota: int
    tanggal_mulai: date
    tanggal_selesai: date
    syarat_ketentuan: str
    narahubung: str
    info_lebih_lanjut: str
    status_kegiatan: StatusKegiatan = StatusKegiatan.DIBUKA
    mbkm_id: int | None = None

    # ---------- Business rules ----------
    def tutup_pendaftaran(self) -> None:
        if self.status_kegiatan in (StatusKegiatan.SELESAI,):
            raise ForbiddenActionError(
                "Kegiatan yang sudah selesai tidak bisa diubah status pendaftarannya"
            )
        self.status_kegiatan = StatusKegiatan.DITUTUP

    def is_pendaftaran_dibuka(self) -> bool:
        return self.status_kegiatan == StatusKegiatan.DIBUKA

    def is_deadline_lewat(self, hari_ini: date | None = None) -> bool:
        hari_ini = hari_ini or date.today()
        return self.deadline_pendaftaran < hari_ini

    def dimiliki_oleh(self, mitra_id: int) -> bool:
        return self.mitra_id == mitra_id


@dataclass
class Magang(KegiatanMBKM):
    bidang: BidangMagang | str = BidangMagang.INFORMATION_TECHNOLOGY
    posisi: str = ""
    nama_perusahaan: str = ""
    logo_url: str | None = None
    penempatan: PenempatanMagang | str = PenempatanMagang.WFO
    kota_lokasi: str = ""
    alamat_lengkap: str = ""
    tipe_gaji: TipeGaji | str = TipeGaji.UNPAID
    gaji_perbulan: float = 0.0
    dokumen_dibutuhkan: list[DokumenLamaran | str] = field(default_factory=list)

    @property
    def lokasi(self) -> str:
        """Alias lama untuk kompatibilitas kode yang masih memakai lokasi."""
        return self.kota_lokasi

    @property
    def uang_saku(self) -> float:
        """Alias lama untuk kompatibilitas kode yang masih memakai uang_saku."""
        return self.gaji_perbulan


@dataclass
class Lomba(KegiatanMBKM):
    bidang: str = ""
    tingkat_lomba: str = ""
    jenis_peserta: str = ""
    jumlah_anggota: int = 1
    hadiah: str = ""


@dataclass
class StudiIndependen(KegiatanMBKM):
    kurikulum: str = ""
    metode_pembelajaran: str = ""
    benefit: str = ""
