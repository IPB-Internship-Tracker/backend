from sqlalchemy.orm import Session

from app.domain.notifikasi import JenisNotifikasi, Notifikasi
from app.models.mahasiswa import MahasiswaORM
from app.models.notifikasi import NotifikasiORM


class NotifikasiRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _to_domain(orm: NotifikasiORM) -> Notifikasi:
        return Notifikasi(
            notifikasi_id=orm.notifikasi_id,
            user_id=orm.user_id,
            judul=orm.judul,
            pesan=orm.pesan,
            jenis_notifikasi=orm.jenis_notifikasi,
            status_baca=orm.status_baca,
            created_at=orm.created_at,
        )

    def get(self, notifikasi_id: int) -> Notifikasi | None:
        orm = self.db.get(NotifikasiORM, notifikasi_id)
        return self._to_domain(orm) if orm else None

    def list_by_user(
        self,
        user_id: int,
        *,
        hanya_belum_dibaca: bool = False,
        jenis: JenisNotifikasi | None = None,
    ) -> list[Notifikasi]:
        q = self.db.query(NotifikasiORM).filter(NotifikasiORM.user_id == user_id)
        if hanya_belum_dibaca:
            q = q.filter(NotifikasiORM.status_baca.is_(False))
        if jenis is not None:
            q = q.filter(NotifikasiORM.jenis_notifikasi == jenis)
        return [self._to_domain(o) for o in q.order_by(NotifikasiORM.created_at.desc()).all()]

    def get_notifikasi_by_mahasiswa(
        self,
        mahasiswa_id: int,
        *,
        hanya_belum_dibaca: bool = False,
        jenis: JenisNotifikasi | None = None,
    ) -> list[Notifikasi]:
        mahasiswa = self.db.get(MahasiswaORM, mahasiswa_id)
        if mahasiswa is None:
            return []
        return self.list_by_user(
            mahasiswa.user_id,
            hanya_belum_dibaca=hanya_belum_dibaca,
            jenis=jenis,
        )

    def hitung_belum_dibaca(self, user_id: int) -> int:
        return (
            self.db.query(NotifikasiORM)
            .filter(
                NotifikasiORM.user_id == user_id,
                NotifikasiORM.status_baca.is_(False),
            )
            .count()
        )

    def buat(self, notifikasi: Notifikasi) -> Notifikasi:
        orm = NotifikasiORM(
            user_id=notifikasi.user_id,
            judul=notifikasi.judul,
            pesan=notifikasi.pesan,
            jenis_notifikasi=notifikasi.jenis_notifikasi,
            status_baca=notifikasi.status_baca,
        )
        self.db.add(orm)
        self.db.flush()
        notifikasi.notifikasi_id = orm.notifikasi_id
        notifikasi.created_at = orm.created_at
        return notifikasi

    def simpan_perubahan(self, notifikasi: Notifikasi) -> Notifikasi:
        orm = self.db.get(NotifikasiORM, notifikasi.notifikasi_id)
        if orm is None:
            raise ValueError(f"Notifikasi id={notifikasi.notifikasi_id} tidak ada")
        orm.status_baca = notifikasi.status_baca
        return notifikasi

    def baca_semua_untuk_user(self, user_id: int) -> None:
        self.db.query(NotifikasiORM).filter(
            NotifikasiORM.user_id == user_id,
            NotifikasiORM.status_baca.is_(False),
        ).update({NotifikasiORM.status_baca: True})

    def commit(self) -> None:
        self.db.commit()
