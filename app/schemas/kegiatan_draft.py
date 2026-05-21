from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.domain.kegiatan import KategoriMBKM


class KegiatanDraftCreate(BaseModel):
    kategori_mbkm: KategoriMBKM
    data: dict[str, Any] = Field(default_factory=dict)


class KegiatanDraftUpdate(BaseModel):
    kategori_mbkm: KategoriMBKM | None = None
    data: dict[str, Any] | None = None


class KegiatanDraftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    draft_id: int
    mitra_id: int
    kategori_mbkm: KategoriMBKM
    data: dict[str, Any]
    created_at: datetime
    updated_at: datetime
