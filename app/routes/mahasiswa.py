from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_mahasiswa, require_admin
from app.domain.mahasiswa import Mahasiswa
from app.repositories import MahasiswaRepository, UserRepository
from app.schemas import MahasiswaDetailResponse, MahasiswaResponse, MahasiswaUpdate
from app.schemas.user import UserResponse


router = APIRouter(prefix="/mahasiswa", tags=["mahasiswa"])


def _detail_response(mhs: Mahasiswa, db: Session) -> dict:
    user = UserRepository(db).get(mhs.user_id)
    return {
        **MahasiswaResponse.model_validate(mhs).model_dump(),
        "user": UserResponse(
            user_id=user.user_id,
            nama=user.nama,
            email=user.email,
            role=user.role,
            created_at=user.created_at,
        ).model_dump(),
    }


@router.get("/me", response_model=MahasiswaDetailResponse)
def profil_saya(
    mahasiswa: Mahasiswa = Depends(get_current_mahasiswa),
    db: Session = Depends(get_db),
):
    return _detail_response(mahasiswa, db)


@router.patch("/me", response_model=MahasiswaResponse)
def update_profil_saya(
    data: MahasiswaUpdate,
    mahasiswa: Mahasiswa = Depends(get_current_mahasiswa),
    db: Session = Depends(get_db),
):
    update_data = data.model_dump(exclude_unset=True)
    mahasiswa.perbarui_profil(**update_data)  # method domain

    repo = MahasiswaRepository(db)
    repo.simpan_perubahan(mahasiswa)

    # sinkronkan nama di User kalau diubah
    if "nama" in update_data:
        user_repo = UserRepository(db)
        user = user_repo.get(mahasiswa.user_id)
        user.nama = update_data["nama"]
        user_repo.simpan_perubahan(user)

    repo.commit()
    return mahasiswa


@router.get("/", response_model=list[MahasiswaResponse])
def list_mahasiswa(
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    return MahasiswaRepository(db).list_semua()


@router.get("/{mahasiswa_id}", response_model=MahasiswaDetailResponse)
def detail_mahasiswa(
    mahasiswa_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    mahasiswa = MahasiswaRepository(db).get(mahasiswa_id)
    if mahasiswa is None:
        raise HTTPException(status_code=404, detail="Mahasiswa tidak ditemukan")
    return _detail_response(mahasiswa, db)