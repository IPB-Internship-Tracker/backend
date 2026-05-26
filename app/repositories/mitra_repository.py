from sqlalchemy.orm import Session, joinedload

from app.domain.mitra import Mitra
from app.domain.user import UserRole
from app.models.mitra import MitraORM


class MitraRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _to_domain(orm: MitraORM) -> Mitra:
        user = orm.user
        return Mitra(
            mitra_id=orm.mitra_id,
            user_id=orm.user_id,
            nama=user.nama if user else "",
            email=user.email if user else "",
            password_hash=user.password if user else "",
            created_at=user.created_at if user else None,
            nama_instansi=orm.nama_instansi,
            jenis_instansi=orm.jenis_instansi,
            alamat=orm.alamat,
            kontak=orm.kontak,
        )

    def get(self, mitra_id: int) -> Mitra | None:
        orm = (
            self.db.query(MitraORM)
            .options(joinedload(MitraORM.user))
            .filter(MitraORM.mitra_id == mitra_id)
            .first()
        )
        return self._to_domain(orm) if orm else None

    def get_by_user_id(self, user_id: int) -> Mitra | None:
        orm = (
            self.db.query(MitraORM)
            .options(joinedload(MitraORM.user))
            .filter(MitraORM.user_id == user_id)
            .first()
        )
        return self._to_domain(orm) if orm else None

    def list_semua(self) -> list[Mitra]:
        rows = self.db.query(MitraORM).options(joinedload(MitraORM.user)).all()
        return [self._to_domain(o) for o in rows]

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
        orm.user.nama = mitra.nama
        if mitra.email:
            orm.user.email = mitra.email.lower()
        if mitra.password_hash:
            orm.user.password = mitra.password_hash
        orm.user.role = UserRole.MITRA
        return mitra

    def commit(self) -> None:
        self.db.commit()
