from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.domain.kegiatan import (
    BidangMagang,
    KategoriMBKM,
    PenempatanMagang,
    StatusKegiatan,
    TipeGaji,
)

if TYPE_CHECKING:
    from app.models.mitra import MitraORM
    from app.models.lamaran import LamaranORM


class KegiatanMBKMORM(Base):
    __tablename__ = "kegiatan_mbkm"

    mbkm_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    mitra_id: Mapped[int] = mapped_column(
        ForeignKey("mitra.mitra_id", ondelete="CASCADE"), nullable=False
    )
    nama_kegiatan: Mapped[str] = mapped_column(String(200), nullable=False)
    deskripsi: Mapped[str] = mapped_column(Text, nullable=False)
    kategori_mbkm: Mapped[KategoriMBKM] = mapped_column(Enum(KategoriMBKM), nullable=False)
    deadline_pendaftaran: Mapped[date] = mapped_column(Date, nullable=False)
    kuota: Mapped[int] = mapped_column(Integer, nullable=False)
    status_kegiatan: Mapped[StatusKegiatan] = mapped_column(
        Enum(StatusKegiatan), default=StatusKegiatan.DIBUKA, nullable=False
    )
    tanggal_mulai: Mapped[date] = mapped_column(Date, nullable=False)
    tanggal_selesai: Mapped[date] = mapped_column(Date, nullable=False)
    syarat_ketentuan: Mapped[str] = mapped_column(Text, nullable=False)
    narahubung: Mapped[str] = mapped_column(String(150), nullable=False)
    info_lebih_lanjut: Mapped[str] = mapped_column(Text, nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "kegiatan_mbkm",
        "polymorphic_on": "kategori_mbkm",
    }

    mitra: Mapped["MitraORM"] = relationship(back_populates="kegiatan")
    lamaran: Mapped[list["LamaranORM"]] = relationship(
        back_populates="kegiatan", cascade="all, delete-orphan"
    )


class MagangORM(KegiatanMBKMORM):
    __tablename__ = "magang"

    mbkm_id: Mapped[int] = mapped_column(
        ForeignKey("kegiatan_mbkm.mbkm_id", ondelete="CASCADE"), primary_key=True
    )
    bidang: Mapped[BidangMagang] = mapped_column(Enum(BidangMagang), nullable=False)
    posisi: Mapped[str] = mapped_column(String(100), nullable=False)
    nama_perusahaan: Mapped[str] = mapped_column(String(200), nullable=False)
    logo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    penempatan: Mapped[PenempatanMagang] = mapped_column(
        Enum(PenempatanMagang), nullable=False
    )
    kota_lokasi: Mapped[str] = mapped_column(String(150), nullable=False)
    alamat_lengkap: Mapped[str] = mapped_column(String(255), nullable=False)
    tipe_gaji: Mapped[TipeGaji] = mapped_column(Enum(TipeGaji), nullable=False)
    gaji_perbulan: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    dokumen_dibutuhkan: Mapped[list[str]] = mapped_column(
        JSON, default=list, nullable=False
    )

    __mapper_args__ = {"polymorphic_identity": KategoriMBKM.MAGANG}


class LombaORM(KegiatanMBKMORM):
    __tablename__ = "lomba"

    mbkm_id: Mapped[int] = mapped_column(
        ForeignKey("kegiatan_mbkm.mbkm_id", ondelete="CASCADE"), primary_key=True
    )
    bidang: Mapped[str] = mapped_column(String(100), nullable=False)
    tingkat_lomba: Mapped[str] = mapped_column(String(100), nullable=False)
    jenis_peserta: Mapped[str] = mapped_column(String(50), nullable=False)
    jumlah_anggota: Mapped[int] = mapped_column(Integer, nullable=False)
    hadiah: Mapped[str] = mapped_column(String(255), nullable=False)

    __mapper_args__ = {"polymorphic_identity": KategoriMBKM.LOMBA}


class StudiIndependenORM(KegiatanMBKMORM):
    __tablename__ = "studi_independen"

    mbkm_id: Mapped[int] = mapped_column(
        ForeignKey("kegiatan_mbkm.mbkm_id", ondelete="CASCADE"), primary_key=True
    )
    kurikulum: Mapped[str] = mapped_column(Text, nullable=False)
    metode_pembelajaran: Mapped[str] = mapped_column(String(100), nullable=False)
    benefit: Mapped[str] = mapped_column(Text, nullable=False)

    __mapper_args__ = {"polymorphic_identity": KategoriMBKM.STUDI_INDEPENDEN}
