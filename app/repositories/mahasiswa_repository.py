from sqlalchemy.orm import Session, joinedload

from app.domain.mahasiswa import Mahasiswa
from app.domain.user import UserRole
from app.models.mahasiswa import MahasiswaORM


class MahasiswaRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _to_domain(orm: MahasiswaORM) -> Mahasiswa:
        user = orm.user
        return Mahasiswa(
            mahasiswa_id=orm.mahasiswa_id,
            user_id=orm.user_id,
            nama=user.nama if user else orm.nama,
            email=user.email if user else "",
            password_hash=user.password if user else "",
            created_at=user.created_at if user else None,
            nim=orm.nim,
            fakultas=orm.fakultas,
            program_studi=orm.program_studi,
            semester=orm.semester,
            foto_profile=orm.foto_profile,
        )

    def get(self, mahasiswa_id: int) -> Mahasiswa | None:
        orm = (
            self.db.query(MahasiswaORM)
            .options(joinedload(MahasiswaORM.user))
            .filter(MahasiswaORM.mahasiswa_id == mahasiswa_id)
            .first()
        )
        return self._to_domain(orm) if orm else None

    def get_by_user_id(self, user_id: int) -> Mahasiswa | None:
        orm = (
            self.db.query(MahasiswaORM)
            .options(joinedload(MahasiswaORM.user))
            .filter(MahasiswaORM.user_id == user_id)
            .first()
        )
        return self._to_domain(orm) if orm else None

    def nim_terdaftar(self, nim: str) -> bool:
        return self.db.query(MahasiswaORM).filter(MahasiswaORM.nim == nim).first() is not None

    def list_semua(self) -> list[Mahasiswa]:
        rows = self.db.query(MahasiswaORM).options(joinedload(MahasiswaORM.user)).all()
        return [self._to_domain(o) for o in rows]

    def buat(self, mahasiswa: Mahasiswa) -> Mahasiswa:
        orm = MahasiswaORM(
            user_id=mahasiswa.user_id,
            nama=mahasiswa.nama,
            nim=mahasiswa.nim,
            fakultas=mahasiswa.fakultas,
            program_studi=mahasiswa.program_studi,
            semester=mahasiswa.semester,
            foto_profile=mahasiswa.foto_profile,
        )
        self.db.add(orm)
        self.db.flush()
        mahasiswa.mahasiswa_id = orm.mahasiswa_id
        return mahasiswa

    def simpan_perubahan(self, mahasiswa: Mahasiswa) -> Mahasiswa:
        orm = self.db.get(MahasiswaORM, mahasiswa.mahasiswa_id)
        if orm is None:
            raise ValueError(f"Mahasiswa id={mahasiswa.mahasiswa_id} tidak ada")
        orm.nama = mahasiswa.nama
        orm.fakultas = mahasiswa.fakultas
        orm.program_studi = mahasiswa.program_studi
        orm.semester = mahasiswa.semester
        orm.foto_profile = mahasiswa.foto_profile
        orm.user.nama = mahasiswa.nama
        if mahasiswa.email:
            orm.user.email = mahasiswa.email.lower()
        if mahasiswa.password_hash:
            orm.user.password = mahasiswa.password_hash
        orm.user.role = UserRole.MAHASISWA
        return mahasiswa

    def commit(self) -> None:
        self.db.commit()
