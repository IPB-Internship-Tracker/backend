from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.domain.lamaran import StatusLamaran

if TYPE_CHECKING:
    from app.models.mahasiswa import MahasiswaORM
    from app.models.kegiatan import KegiatanMBKMORM
    from app.models.logbook import LogbookORM


class LamaranORM(Base):
    __tablename__ = "lamaran"

    lamaran_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    mahasiswa_id: Mapped[int] = mapped_column(
        ForeignKey("mahasiswa.mahasiswa_id", ondelete="CASCADE"), nullable=False
    )
    mbkm_id: Mapped[int] = mapped_column(
        ForeignKey("kegiatan_mbkm.mbkm_id", ondelete="CASCADE"), nullable=False
    )
    berkas_pendaftaran: Mapped[dict[str, str]] = mapped_column(JSON, nullable=False)
    tanggal_daftar: Mapped[date] = mapped_column(
        Date, server_default=func.current_date(), nullable=False
    )
    status_pendaftaran: Mapped[StatusLamaran] = mapped_column(
        Enum(StatusLamaran), default=StatusLamaran.TELAH_MENDAFTAR, nullable=False
    )

    mahasiswa: Mapped["MahasiswaORM"] = relationship(back_populates="lamaran")
    kegiatan: Mapped["KegiatanMBKMORM"] = relationship(back_populates="lamaran")
    logbook: Mapped[list["LogbookORM"]] = relationship(
        back_populates="lamaran", cascade="all, delete-orphan"
    )
