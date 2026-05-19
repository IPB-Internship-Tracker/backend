"""
ORM layer hanya kolom database, tidak ada method bisnis.
Business logic ada di app.domain.user.User.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.domain.user import UserRole

if TYPE_CHECKING:
    from app.models.mahasiswa import MahasiswaORM
    from app.models.mitra import MitraORM
    from app.models.notifikasi import NotifikasiORM


class UserORM(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nama: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    mahasiswa: Mapped[Optional["MahasiswaORM"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    mitra: Mapped[Optional["MitraORM"]] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    notifikasi: Mapped[list["NotifikasiORM"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )