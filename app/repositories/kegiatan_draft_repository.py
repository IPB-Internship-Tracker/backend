from __future__ import annotations

from sqlalchemy.orm import Session

from app.domain.kegiatan_draft import KegiatanDraft
from app.models.kegiatan_draft import KegiatanDraftORM


class KegiatanDraftRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _to_domain(orm: KegiatanDraftORM) -> KegiatanDraft:
        return KegiatanDraft(
            draft_id=orm.draft_id,
            mitra_id=orm.mitra_id,
            kategori_mbkm=orm.kategori_mbkm,
            data=dict(orm.data or {}),
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    def buat(self, draft: KegiatanDraft) -> KegiatanDraft:
        orm = KegiatanDraftORM(
            mitra_id=draft.mitra_id,
            kategori_mbkm=draft.kategori_mbkm,
            data=draft.data,
        )
        self.db.add(orm)
        self.db.flush()
        self.db.refresh(orm)
        return self._to_domain(orm)

    def get(self, draft_id: int) -> KegiatanDraft | None:
        orm = self.db.get(KegiatanDraftORM, draft_id)
        return self._to_domain(orm) if orm else None

    def list_by_mitra(self, mitra_id: int) -> list[KegiatanDraft]:
        rows = (
            self.db.query(KegiatanDraftORM)
            .filter(KegiatanDraftORM.mitra_id == mitra_id)
            .order_by(KegiatanDraftORM.updated_at.desc(), KegiatanDraftORM.draft_id.desc())
            .all()
        )
        return [self._to_domain(row) for row in rows]

    def simpan_perubahan(self, draft: KegiatanDraft) -> KegiatanDraft:
        orm = self.db.get(KegiatanDraftORM, draft.draft_id)
        if orm is None:
            raise ValueError(f"Draft id={draft.draft_id} tidak ada")

        orm.kategori_mbkm = draft.kategori_mbkm
        orm.data = draft.data
        self.db.flush()
        self.db.refresh(orm)
        return self._to_domain(orm)

    def hapus(self, draft_id: int) -> None:
        orm = self.db.get(KegiatanDraftORM, draft_id)
        if orm is not None:
            self.db.delete(orm)

    def commit(self) -> None:
        self.db.commit()
