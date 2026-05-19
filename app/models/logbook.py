from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.lamaran import LamaranORM


class LogbookORM(Base):
    __tablename__ = "logbook"

    logbook_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    lamaran_id: Mapped[int] = mapped_column(
        ForeignKey("lamaran.lamaran_id", ondelete="CASCADE"), nullable=False
    )
    foto: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    aktivitas: Mapped[str] = mapped_column(Text, nullable=False)
    durasi: Mapped[int] = mapped_column(Integer, nullable=False)
    tanggal: Mapped[date] = mapped_column(Date, nullable=False)

    lamaran: Mapped["LamaranORM"] = relationship(back_populates="logbook")