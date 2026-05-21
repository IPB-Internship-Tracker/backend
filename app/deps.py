"""
FastAPI dependencies untuk otentikasi dan otorisasi.
Mengembalikan DOMAIN object (bukan ORM) — routes tidak pernah menyentuh ORM.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.domain.mahasiswa import Mahasiswa
from app.domain.mitra import Mitra
from app.domain.user import User, UserRole
from app.repositories import MahasiswaRepository, MitraRepository, UserRepository
from app.security import decode_access_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Baca JWT, kembalikan User (domain)."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token tidak valid atau sudah kadaluarsa",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
    except ValueError:
        raise credentials_exception

    raw_user_id = payload.get("sub")
    if raw_user_id is None:
        raise credentials_exception

    user = UserRepository(db).get(int(raw_user_id))
    if user is None:
        raise credentials_exception
    return user


def require_role(*roles: UserRole):
    def _checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            allowed = ", ".join(r.value for r in roles)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Akses ditolak. Hanya role {allowed} yang diizinkan.",
            )
        return user
    return _checker


def get_current_mahasiswa(
    user: User = Depends(require_role(UserRole.MAHASISWA)),
    db: Session = Depends(get_db),
) -> Mahasiswa:
    mahasiswa = MahasiswaRepository(db).get_by_user_id(user.user_id)
    if mahasiswa is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil mahasiswa tidak ditemukan",
        )
    return mahasiswa


def get_current_mitra(
    user: User = Depends(require_role(UserRole.MITRA)),
    db: Session = Depends(get_db),
) -> Mitra:
    mitra = MitraRepository(db).get_by_user_id(user.user_id)
    if mitra is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profil mitra tidak ditemukan",
        )
    return mitra
