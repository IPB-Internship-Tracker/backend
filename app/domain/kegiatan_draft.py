from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.domain.kegiatan import KategoriMBKM


@dataclass
class KegiatanDraft:
    """Draft form kegiatan milik mitra sebelum dipublikasikan."""

    mitra_id: int
    kategori_mbkm: KategoriMBKM
    data: dict[str, Any] = field(default_factory=dict)
    draft_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def edit(
        self,
        *,
        kategori_mbkm: KategoriMBKM | None = None,
        data: dict[str, Any] | None = None,
    ) -> None:
        if kategori_mbkm is not None:
            self.kategori_mbkm = kategori_mbkm
        if data is not None:
            self.data.update(data)

    def hapus(self) -> "KegiatanDraft":
        return self

    def dimiliki_oleh(self, mitra_id: int) -> bool:
        return self.mitra_id == mitra_id
