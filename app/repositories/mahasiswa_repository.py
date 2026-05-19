from sqlalchemy.orm import Session

from app.domain.mahasiswa import Mahasiswa
from app.models.mahasiswa import MahasiswaORM


class MahasiswaRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _to_domain(orm: MahasiswaORM) -> Mahasiswa:
        return Mahasiswa(
            mahasiswa_id=orm.mahasiswa_id,
            user_id=orm.user_id,
            nama=orm.nama,
            nim=orm.nim,
            fakultas=orm.fakultas,
            program_studi=orm.program_studi,
            angkatan=orm.angkatan,
        )

    def get(self, mahasiswa_id: int) -> Mahasiswa | None:
        orm = self.db.get(MahasiswaORM, mahasiswa_id)
        return self._to_domain(orm) if orm else None

    def get_by_user_id(self, user_id: int) -> Mahasiswa | None:
        orm = self.db.query(MahasiswaORM).filter(MahasiswaORM.user_id == user_id).first()
        return self._to_domain(orm) if orm else None

    def nim_terdaftar(self, nim: str) -> bool:
        return self.db.query(MahasiswaORM).filter(MahasiswaORM.nim == nim).first() is not None

    def list_semua(self) -> list[Mahasiswa]:
        return [self._to_domain(o) for o in self.db.query(MahasiswaORM).all()]

    def buat(self, mahasiswa: Mahasiswa) -> Mahasiswa:
        orm = MahasiswaORM(
            user_id=mahasiswa.user_id,
            nama=mahasiswa.nama,
            nim=mahasiswa.nim,
            fakultas=mahasiswa.fakultas,
            program_studi=mahasiswa.program_studi,
            angkatan=mahasiswa.angkatan,
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
        orm.angkatan = mahasiswa.angkatan
        return mahasiswa

    def commit(self) -> None:
        self.db.commit()