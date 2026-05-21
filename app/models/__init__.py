"""
ORM layer, kumpulan SQLAlchemy model untuk persistence.
NOTE: Semua class ORM di-suffix dengan `ORM` untuk membedakan dengan domain.
Business logic ada di app.domain, BUKAN di sini.
"""
from app.models.user import UserORM
from app.models.mahasiswa import MahasiswaORM
from app.models.mitra import MitraORM
from app.models.kegiatan import KegiatanMBKMORM, MagangORM, LombaORM, StudiIndependenORM
from app.models.kegiatan_draft import KegiatanDraftORM
from app.models.lamaran import LamaranORM
from app.models.logbook import LogbookORM
from app.models.notifikasi import NotifikasiORM

__all__ = [
    "UserORM",
    "MahasiswaORM",
    "MitraORM",
    "KegiatanMBKMORM",
    "MagangORM",
    "LombaORM",
    "StudiIndependenORM",
    "KegiatanDraftORM",
    "LamaranORM",
    "LogbookORM",
    "NotifikasiORM",
]
