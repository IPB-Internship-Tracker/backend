from sqlalchemy.orm import Session

from app.domain.mitra import Mitra
from app.models.mitra import MitraORM


class MitraRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _to_domain(orm: MitraORM) -> Mitra:
        return Mitra(
            mitra_id=orm.mitra_id,
            user_id=orm.user_id,
            nama_instansi=orm.nama_instansi,
            jenis_instansi=orm.jenis_instansi,
            alamat=orm.alamat,
            kontak=orm.kontak,
        )

    def get(self, mitra_id: int) -> Mitra | None:
        orm = self.db.get(MitraORM, mitra_id)
        return self._to_domain(orm) if orm else None

    def get_by_user_id(self, user_id: int) -> Mitra | None:
        orm = self.db.query(MitraORM).filter(MitraORM.user_id == user_id).first()
        return self._to_domain(orm) if orm else None

    def list_semua(self) -> list[Mitra]:
        return [self._to_domain(o) for o in self.db.query(MitraORM).all()]

    def buat(self, mitra: Mitra) -> Mitra:
        orm = MitraORM(
            user_id=mitra.user_id,
            nama_instansi=mitra.nama_instansi,
            jenis_instansi=mitra.jenis_instansi,
            alamat=mitra.alamat,
            kontak=mitra.kontak,
        )
        self.db.add(orm)
        self.db.flush()
        mitra.mitra_id = orm.mitra_id
        return mitra

    def simpan_perubahan(self, mitra: Mitra) -> Mitra:
        orm = self.db.get(MitraORM, mitra.mitra_id)
        if orm is None:
            raise ValueError(f"Mitra id={mitra.mitra_id} tidak ada")
        orm.nama_instansi = mitra.nama_instansi
        orm.jenis_instansi = mitra.jenis_instansi
        orm.alamat = mitra.alamat
        orm.kontak = mitra.kontak
        return mitra

    def commit(self) -> None:
        self.db.commit()