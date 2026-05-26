from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    ResetPasswordRequest,
    TokenResponse,
    TokenPayload,
)
from app.schemas.user import UserResponse, UserUpdate, ChangePasswordRequest
from app.schemas.mahasiswa import (
    MahasiswaRegister,
    MahasiswaUpdate,
    MahasiswaResponse,
    MahasiswaDetailResponse,
)
from app.schemas.mitra import (
    MitraRegister,
    MitraUpdate,
    MitraResponse,
    MitraDetailResponse,
)
from app.schemas.kegiatan import (
    MagangCreate,
    MagangUpdate,
    MagangResponse,
    LombaCreate,
    LombaUpdate,
    LombaResponse,
    StudiIndependenCreate,
    StudiIndependenUpdate,
    StudiIndependenResponse,
    KegiatanListResponse,
    KegiatanResponse,
)
from app.schemas.kegiatan_draft import (
    KegiatanDraftCreate,
    KegiatanDraftUpdate,
    KegiatanDraftResponse,
)
from app.schemas.lamaran import (
    LamaranCreate,
    LamaranStatusUpdate,
    LamaranResponse,
    LamaranDetailResponse,
)
from app.schemas.logbook import LogbookCreate, LogbookUpdate, LogbookResponse
from app.schemas.notifikasi import NotifikasiCreate, NotifikasiResponse

__all__ = [
    "LoginRequest",
    "ForgotPasswordRequest",
    "ResetPasswordRequest",
    "TokenResponse",
    "TokenPayload",
    "UserResponse",
    "UserUpdate",
    "ChangePasswordRequest",
    "MahasiswaRegister",
    "MahasiswaUpdate",
    "MahasiswaResponse",
    "MahasiswaDetailResponse",
    "MitraRegister",
    "MitraUpdate",
    "MitraResponse",
    "MitraDetailResponse",
    "MagangCreate",
    "MagangUpdate",
    "MagangResponse",
    "LombaCreate",
    "LombaUpdate",
    "LombaResponse",
    "StudiIndependenCreate",
    "StudiIndependenUpdate",
    "StudiIndependenResponse",
    "KegiatanListResponse",
    "KegiatanResponse",
    "KegiatanDraftCreate",
    "KegiatanDraftUpdate",
    "KegiatanDraftResponse",
    "LamaranCreate",
    "LamaranStatusUpdate",
    "LamaranResponse",
    "LamaranDetailResponse",
    "LogbookCreate",
    "LogbookUpdate",
    "LogbookResponse",
    "NotifikasiCreate",
    "NotifikasiResponse",
]
