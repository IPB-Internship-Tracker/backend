from dataclasses import dataclass
from datetime import date

from app.domain.exceptions import ForbiddenActionError


@dataclass
class Logbook:
    lamaran_id: int
    aktivitas: str
    durasi: int  # menit
    tanggal: date
    foto: str | None = None
    logbook_id: int | None = None

    def __post_init__(self) -> None:
        # Rule: durasi harus masuk akal (0 < durasi <= 24 jam)
        if not (0 < self.durasi <= 24 * 60):
            raise ForbiddenActionError(
                "Durasi logbook harus > 0 menit dan <= 1440 menit (24 jam)"
            )