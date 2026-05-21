from sqlalchemy.orm import Session

from app.domain.logbook import Logbook
from app.models.logbook import LogbookORM


class LogbookRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _to_domain(orm: LogbookORM) -> Logbook:
        # lewati validasi __post_init__ karena data dari DB dianggap sudah valid.
        # (Rule enforcement di domain saat CREATE, bukan saat load dari DB.)
        logbook = object.__new__(Logbook)
        logbook.logbook_id = orm.logbook_id
        logbook.lamaran_id = orm.lamaran_id
        logbook.foto = orm.foto
        logbook.aktivitas = orm.aktivitas
        logbook.durasi = orm.durasi
        logbook.tanggal = orm.tanggal
        return logbook

    def get(self, logbook_id: int) -> Logbook | None:
        orm = self.db.get(LogbookORM, logbook_id)
        return self._to_domain(orm) if orm else None

    def get_logbook_by_id(self, logbook_id: int) -> Logbook | None:
        return self.get(logbook_id)

    def list_by_lamaran(self, lamaran_id: int) -> list[Logbook]:
        q = (
            self.db.query(LogbookORM)
            .filter(LogbookORM.lamaran_id == lamaran_id)
            .order_by(LogbookORM.tanggal.desc())
        )
        return [self._to_domain(o) for o in q.all()]

    def get_logbook_by_lamaran(self, lamaran_id: int) -> list[Logbook]:
        return self.list_by_lamaran(lamaran_id)

    def buat(self, logbook: Logbook) -> Logbook:
        orm = LogbookORM(
            lamaran_id=logbook.lamaran_id,
            foto=logbook.foto,
            aktivitas=logbook.aktivitas,
            durasi=logbook.durasi,
            tanggal=logbook.tanggal,
        )
        self.db.add(orm)
        self.db.flush()
        logbook.logbook_id = orm.logbook_id
        return logbook

    def simpan_perubahan(self, logbook: Logbook) -> Logbook:
        orm = self.db.get(LogbookORM, logbook.logbook_id)
        if orm is None:
            raise ValueError(f"Logbook id={logbook.logbook_id} tidak ada")
        orm.foto = logbook.foto
        orm.aktivitas = logbook.aktivitas
        orm.durasi = logbook.durasi
        orm.tanggal = logbook.tanggal
        return logbook

    def hapus(self, logbook_id: int) -> None:
        orm = self.db.get(LogbookORM, logbook_id)
        if orm is not None:
            self.db.delete(orm)

    def commit(self) -> None:
        self.db.commit()
