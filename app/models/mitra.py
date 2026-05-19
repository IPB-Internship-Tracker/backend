from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import UserORM
    from app.models.kegiatan import KegiatanMBKMORM


class MitraORM(Base):
    __tablename__ = "mitra"

    mitra_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False
    )
    nama_instansi: Mapped[str] = mapped_column(String(200), nullable=False)
    jenis_instansi: Mapped[str] = mapped_column(String(100), nullable=False)
    alamat: Mapped[str] = mapped_column(String(255), nullable=False)
    kontak: Mapped[str] = mapped_column(String(50), nullable=False)

    user: Mapped["UserORM"] = relationship(back_populates="mitra")
    kegiatan: Mapped[list["KegiatanMBKMORM"]] = relationship(
        back_populates="mitra", cascade="all, delete-orphan"
    )