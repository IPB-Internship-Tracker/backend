from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import UserORM
    from app.models.lamaran import LamaranORM


class MahasiswaORM(Base):
    __tablename__ = "mahasiswa"

    mahasiswa_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False
    )
    nama: Mapped[str] = mapped_column(String(150), nullable=False)
    nim: Mapped[str] = mapped_column(String(11), unique=True, nullable=False, index=True)
    fakultas: Mapped[str] = mapped_column(String(100), nullable=False)
    program_studi: Mapped[str] = mapped_column(String(100), nullable=False)
    semester: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    foto_profile: Mapped[str | None] = mapped_column(String(255), nullable=True)

    user: Mapped["UserORM"] = relationship(back_populates="mahasiswa")
    lamaran: Mapped[list["LamaranORM"]] = relationship(
        back_populates="mahasiswa", cascade="all, delete-orphan"
    )
