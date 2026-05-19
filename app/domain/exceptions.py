"""
Exception khusus untuk pelanggaran aturan bisnis di domain.
Route layer akan nangkep ini dan mengubahnya jadi HTTPException.
"""


class DomainError(Exception):
    """Raised ketika ada pelanggaran aturan bisnis di domain layer."""


class NotFoundError(DomainError):
    """Raised ketika entitas tidak ditemukan."""


class ForbiddenActionError(DomainError):
    """Raised ketika aksi tidak diperbolehkan (misal: state transition ilegal)."""