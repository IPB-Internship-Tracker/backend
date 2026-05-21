from sqlalchemy.orm import Session

from app.domain.kegiatan import DokumenLamaran
from app.domain.lamaran import Lamaran, StatusLamaran
from app.models.lamaran import LamaranORM


class LamaranRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _berkas_to_domain(raw: dict[str, str] | str | None) -> dict[DokumenLamaran | str, str]:
        if raw is None:
            return {}
        if isinstance(raw, str):
            return {DokumenLamaran.CV: raw}
        hasil: dict[DokumenLamaran | str, str] = {}
        for dokumen, berkas in raw.items():
            try:
                hasil[DokumenLamaran(dokumen)] = berkas
            except ValueError:
                hasil[dokumen] = berkas
        return hasil

    @staticmethod
    def _berkas_to_storage(berkas_pendaftaran: dict[DokumenLamaran | str, str]) -> dict[str, str]:
        return {
            dokumen.value if isinstance(dokumen, DokumenLamaran) else str(dokumen): berkas
            for dokumen, berkas in berkas_pendaftaran.items()
        }

    @staticmethod
    def _to_domain(orm: LamaranORM) -> Lamaran:
        return Lamaran(
            lamaran_id=orm.lamaran_id,
            mahasiswa_id=orm.mahasiswa_id,
            mbkm_id=orm.mbkm_id,
            berkas_pendaftaran=LamaranRepository._berkas_to_domain(orm.berkas_pendaftaran),
            tanggal_daftar=orm.tanggal_daftar,
            status_pendaftaran=orm.status_pendaftaran,
        )

    def get(self, lamaran_id: int) -> Lamaran | None:
        orm = self.db.get(LamaranORM, lamaran_id)
        return self._to_domain(orm) if orm else None

    def list_by_mahasiswa(
        self,
        mahasiswa_id: int,
        status: StatusLamaran | None = None,
    ) -> list[Lamaran]:
        q = self.db.query(LamaranORM).filter(LamaranORM.mahasiswa_id == mahasiswa_id)
        if status is not None:
            q = q.filter(LamaranORM.status_pendaftaran == status)
        return [self._to_domain(o) for o in q.order_by(LamaranORM.tanggal_daftar.desc()).all()]

    def get_lamaran_by_mahasiswa(
        self,
        mahasiswa_id: int,
        status: StatusLamaran | None = None,
    ) -> list[Lamaran]:
        return self.list_by_mahasiswa(mahasiswa_id, status=status)

    def list_by_kegiatan(self, mbkm_id: int) -> list[Lamaran]:
        q = self.db.query(LamaranORM).filter(LamaranORM.mbkm_id == mbkm_id)
        return [self._to_domain(o) for o in q.order_by(LamaranORM.tanggal_daftar.desc()).all()]

    def cari_duplikat(self, mahasiswa_id: int, mbkm_id: int) -> Lamaran | None:
        orm = (
            self.db.query(LamaranORM)
            .filter(LamaranORM.mahasiswa_id == mahasiswa_id, LamaranORM.mbkm_id == mbkm_id)
            .first()
        )
        return self._to_domain(orm) if orm else None

    def hitung_diterima(self, mbkm_id: int) -> int:
        return (
            self.db.query(LamaranORM)
            .filter(
                LamaranORM.mbkm_id == mbkm_id,
                LamaranORM.status_pendaftaran == StatusLamaran.DITERIMA,
            )
            .count()
        )

    def buat(self, lamaran: Lamaran) -> Lamaran:
        orm = LamaranORM(
            mahasiswa_id=lamaran.mahasiswa_id,
            mbkm_id=lamaran.mbkm_id,
            berkas_pendaftaran=self._berkas_to_storage(lamaran.berkas_pendaftaran),
            status_pendaftaran=lamaran.status_pendaftaran,
        )
        self.db.add(orm)
        self.db.flush()
        lamaran.lamaran_id = orm.lamaran_id
        lamaran.tanggal_daftar = orm.tanggal_daftar
        return lamaran

    def simpan_perubahan(self, lamaran: Lamaran) -> Lamaran:
        orm = self.db.get(LamaranORM, lamaran.lamaran_id)
        if orm is None:
            raise ValueError(f"Lamaran id={lamaran.lamaran_id} tidak ada")
        orm.status_pendaftaran = lamaran.status_pendaftaran
        orm.berkas_pendaftaran = self._berkas_to_storage(lamaran.berkas_pendaftaran)
        return lamaran

    def commit(self) -> None:
        self.db.commit()
