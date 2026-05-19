import enum
from dataclasses import dataclass
from datetime import datetime


class JenisNotifikasi(str, enum.Enum):
    REMINDER_LOGBOOK_HARIAN = "reminder_logbook_harian"
    REMINDER_DEADLINE_LOGBOOK = "reminder_deadline_logbook"
    STATUS_LAMARAN = "status_lamaran"
    REMINDER_CONVERT_SKS = "reminder_convert_sks"


@dataclass
class Notifikasi:
    user_id: int
    judul: str
    pesan: str
    jenis_notifikasi: JenisNotifikasi
    status_baca: bool = False
    created_at: datetime | None = None
    notifikasi_id: int | None = None

    def tandai_sudah_dibaca(self) -> None:
        self.status_baca = True