from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.domain.kegiatan import KategoriMBKM


class KegiatanDraftORM(Base):
    __tablename__ = "kegiatan_draft"

    draft_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    mitra_id: Mapped[int] = mapped_column(
        ForeignKey("mitra.mitra_id", ondelete="CASCADE"), nullable=False, index=True
    )
    kategori_mbkm: Mapped[KategoriMBKM] = mapped_column(Enum(KategoriMBKM), nullable=False)
    data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
