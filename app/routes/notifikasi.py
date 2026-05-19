from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.domain.notifikasi import JenisNotifikasi
from app.domain.user import User
from app.repositories import NotifikasiRepository
from app.schemas import NotifikasiResponse


router = APIRouter(prefix="/notifikasi", tags=["notifikasi"])


@router.get("/saya", response_model=list[NotifikasiResponse])
def list_notifikasi_saya(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    hanya_belum_dibaca: bool = False,
    jenis: JenisNotifikasi | None = None,
):
    return NotifikasiRepository(db).list_by_user(
        user.user_id, hanya_belum_dibaca=hanya_belum_dibaca, jenis=jenis
    )


@router.get("/saya/count-belum-dibaca")
def hitung_belum_dibaca(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    return {"jumlah": NotifikasiRepository(db).hitung_belum_dibaca(user.user_id)}


@router.patch("/{notifikasi_id}/baca", response_model=NotifikasiResponse)
def tandai_dibaca(
    notifikasi_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = NotifikasiRepository(db)
    notif = repo.get(notifikasi_id)
    if notif is None:
        raise HTTPException(status_code=404, detail="Notifikasi tidak ditemukan")
    if notif.user_id != user.user_id:
        raise HTTPException(status_code=403, detail="Bukan notifikasi Anda")

    notif.tandai_sudah_dibaca()  # method domain
    repo.simpan_perubahan(notif)
    repo.commit()
    return notif


@router.post("/saya/baca-semua", status_code=204)
def baca_semua(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = NotifikasiRepository(db)
    repo.baca_semua_untuk_user(user.user_id)
    repo.commit()