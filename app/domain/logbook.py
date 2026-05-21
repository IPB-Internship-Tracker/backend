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
        # Rule: (0 < durasi <= 24 jam)
        if not (0 < self.durasi <= 24 * 60):
            raise ForbiddenActionError(
                "Durasi logbook harus > 0 menit dan <= 1440 menit (24 jam)"
            )

    @property
    def kegiatan_perhari(self) -> str:
        """Alias class diagram untuk aktivitas."""
        return self.aktivitas

    @kegiatan_perhari.setter
    def kegiatan_perhari(self, value: str) -> None:
        self.aktivitas = value

    def tambah_logbook(self) -> "Logbook":
        return self

    def edit(self, **perubahan) -> None:
        for field_name, value in perubahan.items():
            setattr(self, field_name, value)
        self.__post_init__()

    def hapus(self) -> "Logbook":
        return self

    def tambah_aktivitas(self, aktivitas: str) -> None:
        self.aktivitas = aktivitas
