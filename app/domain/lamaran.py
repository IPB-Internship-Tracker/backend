"""
Domain entity: Lamaran.
Business rule: aturan perubahan status.
"""

import enum
from dataclasses import dataclass
from datetime import date

from app.domain.exceptions import ForbiddenActionError


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
    berkas_pendaftaran: str
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

    def is_diterima(self) -> bool:
        return self.status_pendaftaran == StatusLamaran.DITERIMA

    def is_final(self) -> bool:
        return self.status_pendaftaran in _FINAL_STATUSES
