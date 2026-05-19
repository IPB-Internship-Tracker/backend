from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_mitra
from app.domain.mitra import Mitra
from app.repositories import MitraRepository, UserRepository
from app.schemas import MitraDetailResponse, MitraResponse, MitraUpdate
from app.schemas.user import UserResponse


router = APIRouter(prefix="/mitra", tags=["mitra"])


def _detail_response(mitra: Mitra, db: Session) -> dict:
    user = UserRepository(db).get(mitra.user_id)
    return {
        **MitraResponse.model_validate(mitra).model_dump(),
        "user": UserResponse(
            user_id=user.user_id,
            nama=user.nama,
            email=user.email,
            role=user.role,
            created_at=user.created_at,
        ).model_dump(),
    }


@router.get("/me", response_model=MitraDetailResponse)
def profil_saya(
    mitra: Mitra = Depends(get_current_mitra),
    db: Session = Depends(get_db),
):
    return _detail_response(mitra, db)


@router.patch("/me", response_model=MitraResponse)
def update_profil_saya(
    data: MitraUpdate,
    mitra: Mitra = Depends(get_current_mitra),
    db: Session = Depends(get_db),
):
    mitra.perbarui_profil(**data.model_dump(exclude_unset=True))
    repo = MitraRepository(db)
    repo.simpan_perubahan(mitra)
    repo.commit()
    return mitra


@router.get("/", response_model=list[MitraResponse])
def list_mitra(db: Session = Depends(get_db)):
    return MitraRepository(db).list_semua()


@router.get("/{mitra_id}", response_model=MitraResponse)
def detail_mitra(mitra_id: int, db: Session = Depends(get_db)):
    mitra = MitraRepository(db).get(mitra_id)
    if mitra is None:
        raise HTTPException(status_code=404, detail="Mitra tidak ditemukan")
    return mitra