from app.repositories.user_repository import UserRepository
from app.repositories.mahasiswa_repository import MahasiswaRepository
from app.repositories.mitra_repository import MitraRepository
from app.repositories.kegiatan_repository import KegiatanRepository
from app.repositories.kegiatan_draft_repository import KegiatanDraftRepository
from app.repositories.lamaran_repository import LamaranRepository
from app.repositories.logbook_repository import LogbookRepository
from app.repositories.notifikasi_repository import NotifikasiRepository

__all__ = [
    "UserRepository",
    "MahasiswaRepository",
    "MitraRepository",
    "KegiatanRepository",
    "KegiatanDraftRepository",
    "LamaranRepository",
    "LogbookRepository",
    "NotifikasiRepository",
]
