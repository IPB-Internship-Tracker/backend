"""
Domain entity: Lamaran.
Business rule: aturan perubahan status.
"""

import enum
from dataclasses import dataclass
from datetime import date

from app.domain.exceptions import ForbiddenActionError
from app.domain.kegiatan import DokumenLamaran


class StatusLamaran(str, enum.Enum):
    TELAH_MENDAFTAR = "telah_mendaftar"
    WAWANCARA = "wawancara"
    DITERIMA = "diterima"
    DITOLAK = "ditolak"

_FINAL_STATUSES = frozenset({
    StatusLamaran.DITERIMA,
    StatusLamaran.DITOLAK,
})


@dataclass
class Lamaran:
    mahasiswa_id: int
    mbkm_id: int
    berkas_pendaftaran: dict[DokumenLamaran | str, str]
    tanggal_daftar: date
    status_pendaftaran: StatusLamaran = StatusLamaran.TELAH_MENDAFTAR
    lamaran_id: int | None = None

    # ---------- Business rules ----------
    def ubah_status(self, status_baru: StatusLamaran) -> None:
        """Ubah status lamaran. Tidak boleh mengubah kalau sudah final."""
        if self.status_pendaftaran in _FINAL_STATUSES:
            raise ForbiddenActionError(
                f"Lamaran sudah berstatus final '{self.status_pendaftaran.value}' "
                "dan tidak bisa diubah"
            )
        self.status_pendaftaran = status_baru

    def get_status(self) -> StatusLamaran:
        return self.status_pendaftaran

    def tambah_berkas(
        self,
        dokumen: DokumenLamaran | str,
        berkas: str | None = None,
    ) -> None:
        if berkas is None:
            berkas = dokumen
            dokumen = DokumenLamaran.CV
        if not berkas:
            raise ForbiddenActionError("Berkas pendaftaran tidak boleh kosong")
        self.berkas_pendaftaran[dokumen] = berkas

    def hapus_berkas(self) -> None:
        self.berkas_pendaftaran = {}

    def validate(self) -> bool:
        return (
            self.mahasiswa_id > 0
            and self.mbkm_id > 0
            and bool(self.berkas_pendaftaran)
            and all(bool(path) for path in self.berkas_pendaftaran.values())
        )

    def is_diterima(self) -> bool:
        return self.status_pendaftaran == StatusLamaran.DITERIMA

    def is_final(self) -> bool:
        return self.status_pendaftaran in _FINAL_STATUSES
