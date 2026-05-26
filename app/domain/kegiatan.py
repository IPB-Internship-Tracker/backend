"""
Domain entity: KegiatanMBKM + subclass (Magang, Lomba, StudiIndependen).
Inheritance di level domain. Tidak ada SQLAlchemy.
"""

import enum
from dataclasses import dataclass, field
from datetime import date


class KategoriMBKM(str, enum.Enum):
    MAGANG = "magang"
    LOMBA = "lomba"
    STUDI_INDEPENDEN = "studi_independen"


class StatusKegiatan(str, enum.Enum):
    REGISTRASI_DIBUKA = "Registrasi Dibuka"
    REGISTRASI_DITUTUP = "Registrasi Ditutup"


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
    status: StatusKegiatan = StatusKegiatan.REGISTRASI_DIBUKA
    mbkm_id: int | None = None

    def __post_init__(self) -> None:
        self.status = self._normalisasi_status(self.status)
        self.sinkronkan_status_deadline()

    @staticmethod
    def _normalisasi_status(status: StatusKegiatan | str) -> StatusKegiatan:
        if isinstance(status, StatusKegiatan):
            return status
        legacy_status = {
            "DIBUKA": StatusKegiatan.REGISTRASI_DIBUKA,
            "dibuka": StatusKegiatan.REGISTRASI_DIBUKA,
            "REGISTRASI_DIBUKA": StatusKegiatan.REGISTRASI_DIBUKA,
            "Registrasi Dibuka": StatusKegiatan.REGISTRASI_DIBUKA,
            "DITUTUP": StatusKegiatan.REGISTRASI_DITUTUP,
            "ditutup": StatusKegiatan.REGISTRASI_DITUTUP,
            "BERLANGSUNG": StatusKegiatan.REGISTRASI_DITUTUP,
            "berlangsung": StatusKegiatan.REGISTRASI_DITUTUP,
            "SELESAI": StatusKegiatan.REGISTRASI_DITUTUP,
            "selesai": StatusKegiatan.REGISTRASI_DITUTUP,
            "REGISTRASI_DITUTUP": StatusKegiatan.REGISTRASI_DITUTUP,
            "Registrasi Ditutup": StatusKegiatan.REGISTRASI_DITUTUP,
        }
        return legacy_status.get(str(status), StatusKegiatan.REGISTRASI_DIBUKA)

    @property
    def kegiatan_id(self) -> int | None:
        """Alias class diagram untuk mbkm_id."""
        return self.mbkm_id

    @kegiatan_id.setter
    def kegiatan_id(self, value: int | None) -> None:
        self.mbkm_id = value

    @property
    def kategori(self) -> KategoriMBKM:
        """Alias class diagram untuk kategori_mbkm."""
        return self.kategori_mbkm

    @kategori.setter
    def kategori(self, value: KategoriMBKM) -> None:
        self.kategori_mbkm = value

    @property
    def info_lebihlanjut(self) -> str:
        """Alias class diagram untuk info_lebih_lanjut."""
        return self.info_lebih_lanjut

    @info_lebihlanjut.setter
    def info_lebihlanjut(self, value: str) -> None:
        self.info_lebih_lanjut = value

    # ---------- Business rules ----------
    def tambah(self) -> "KegiatanMBKM":
        """Kembalikan entity untuk disimpan oleh repository."""
        return self

    def edit(self, **perubahan) -> None:
        for field_name, value in perubahan.items():
            setattr(self, field_name, value)
        self.status = self._normalisasi_status(self.status)
        self.sinkronkan_status_deadline()

    def hapus(self) -> "KegiatanMBKM":
        """Validasi domain sebelum repository menghapus entity."""
        self.sinkronkan_status_deadline()
        return self

    def tutup_pendaftaran(self) -> None:
        """Kompatibilitas aksi lama untuk menutup registrasi secara manual."""
        self.status = StatusKegiatan.REGISTRASI_DITUTUP

    def is_pendaftaran_dibuka(self) -> bool:
        self.sinkronkan_status_deadline()
        return self.status == StatusKegiatan.REGISTRASI_DIBUKA

    def sinkronkan_status_deadline(
        self, hari_ini: date | None = None
    ) -> StatusKegiatan:
        if self.is_deadline_lewat(hari_ini):
            self.status = StatusKegiatan.REGISTRASI_DITUTUP
        return self.status

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

    @lokasi.setter
    def lokasi(self, value: str) -> None:
        self.kota_lokasi = value

    @property
    def uang_saku(self) -> float:
        """Alias lama untuk kompatibilitas kode yang masih memakai uang_saku."""
        return self.gaji_perbulan

    @uang_saku.setter
    def uang_saku(self, value: float) -> None:
        self.gaji_perbulan = value


@dataclass
class Lomba(KegiatanMBKM):
    bidang: str = ""
    poster: str = ""


@dataclass
class StudiIndependen(KegiatanMBKM):
    bidang: str = ""
    poster: str = ""
