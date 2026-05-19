from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_mahasiswa, get_current_mitra, get_current_user
from app.domain.exceptions import ForbiddenActionError
from app.domain.lamaran import Lamaran, StatusLamaran
from app.domain.mahasiswa import Mahasiswa
from app.domain.mitra import Mitra
from app.domain.notifikasi import JenisNotifikasi, Notifikasi
from app.domain.user import User, UserRole
from app.repositories import (
    KegiatanRepository,
    LamaranRepository,
    MahasiswaRepository,
    NotifikasiRepository,
)
from app.schemas import (
    LamaranCreate,
    LamaranDetailResponse,
    LamaranResponse,
    LamaranStatusUpdate,
)
from app.schemas.kegiatan import KegiatanListResponse
from app.schemas.mahasiswa import MahasiswaResponse


router = APIRouter(prefix="/lamaran", tags=["lamaran"])


def _detail_response(lamaran: Lamaran, db: Session) -> dict:
    mhs = MahasiswaRepository(db).get(lamaran.mahasiswa_id)
    kegiatan = KegiatanRepository(db).get(lamaran.mbkm_id)
    return {
        **LamaranResponse.model_validate(lamaran).model_dump(),
        "mahasiswa": MahasiswaResponse.model_validate(mhs).model_dump(),
        "kegiatan": KegiatanListResponse.model_validate(kegiatan).model_dump(),
    }


# ---------- Mahasiswa daftar ----------
@router.post("/", response_model=LamaranResponse, status_code=201)
def buat_lamaran(
    data: LamaranCreate,
    mahasiswa: Mahasiswa = Depends(get_current_mahasiswa),
    db: Session = Depends(get_db),
):
    kegiatan_repo = KegiatanRepository(db)
    lamaran_repo = LamaranRepository(db)

    kegiatan = kegiatan_repo.get(data.mbkm_id)
    if kegiatan is None:
        raise HTTPException(status_code=404, detail="Kegiatan tidak ditemukan")

    # pakai method domain untuk cek business rule
    if not kegiatan.is_pendaftaran_dibuka():
        raise HTTPException(
            status_code=400,
            detail=f"Pendaftaran kegiatan ini {kegiatan.status_kegiatan.value}",
        )
    if kegiatan.is_deadline_lewat():
        raise HTTPException(status_code=400, detail="Deadline pendaftaran sudah lewat")

    if lamaran_repo.cari_duplikat(mahasiswa.mahasiswa_id, data.mbkm_id) is not None:
        raise HTTPException(status_code=409, detail="Anda sudah mendaftar ke kegiatan ini")

    if lamaran_repo.hitung_diterima(data.mbkm_id) >= kegiatan.kuota:
        raise HTTPException(status_code=400, detail="Kuota kegiatan sudah penuh")

    lamaran = Lamaran(
        mahasiswa_id=mahasiswa.mahasiswa_id,
        mbkm_id=data.mbkm_id,
        berkas_pendaftaran=data.berkas_pendaftaran,
        tanggal_daftar=date.today(),
    )
    lamaran_repo.buat(lamaran)
    lamaran_repo.commit()
    return lamaran


# ---------- Mahasiswa list lamaran sendiri ----------
@router.get("/saya", response_model=list[LamaranResponse])
def lamaran_saya(
    mahasiswa: Mahasiswa = Depends(get_current_mahasiswa),
    db: Session = Depends(get_db),
    status_pendaftaran: StatusLamaran | None = None,
):
    return LamaranRepository(db).list_by_mahasiswa(
        mahasiswa.mahasiswa_id, status=status_pendaftaran
    )


# ---------- Mitra list lamaran ke kegiatannya ----------
@router.get("/kegiatan/{mbkm_id}", response_model=list[LamaranDetailResponse])
def lamaran_untuk_kegiatan(
    mbkm_id: int,
    mitra: Mitra = Depends(get_current_mitra),
    db: Session = Depends(get_db),
):
    kegiatan = KegiatanRepository(db).get(mbkm_id)
    if kegiatan is None:
        raise HTTPException(status_code=404, detail="Kegiatan tidak ditemukan")
    if not kegiatan.dimiliki_oleh(mitra.mitra_id):
        raise HTTPException(status_code=403, detail="Anda bukan pemilik kegiatan ini")

    lamarans = LamaranRepository(db).list_by_kegiatan(mbkm_id)
    return [_detail_response(l, db) for l in lamarans]


# ---------- Detail lamaran ----------
@router.get("/{lamaran_id}", response_model=LamaranDetailResponse)
def detail_lamaran(
    lamaran_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lamaran = LamaranRepository(db).get(lamaran_id)
    if lamaran is None:
        raise HTTPException(status_code=404, detail="Lamaran tidak ditemukan")

    # authorization: mahasiswa pemilik atau mitra pemilik kegiatan
    if user.is_mahasiswa():
        mhs = MahasiswaRepository(db).get_by_user_id(user.user_id)
        if mhs is None or lamaran.mahasiswa_id != mhs.mahasiswa_id:
            raise HTTPException(status_code=403, detail="Bukan lamaran Anda")
    elif user.is_mitra():
        from app.repositories import MitraRepository
        mitra = MitraRepository(db).get_by_user_id(user.user_id)
        kegiatan = KegiatanRepository(db).get(lamaran.mbkm_id)
        if mitra is None or kegiatan is None or not kegiatan.dimiliki_oleh(mitra.mitra_id):
            raise HTTPException(status_code=403, detail="Bukan lamaran untuk kegiatan Anda")
    # admin: boleh semua

    return _detail_response(lamaran, db)


# ---------- Mitra ubah status -> trigger notifikasi ----------
@router.patch("/{lamaran_id}/status", response_model=LamaranResponse)
def ubah_status_lamaran(
    lamaran_id: int,
    data: LamaranStatusUpdate,
    mitra: Mitra = Depends(get_current_mitra),
    db: Session = Depends(get_db),
):
    lamaran_repo = LamaranRepository(db)
    notif_repo = NotifikasiRepository(db)

    lamaran = lamaran_repo.get(lamaran_id)
    if lamaran is None:
        raise HTTPException(status_code=404, detail="Lamaran tidak ditemukan")

    kegiatan = KegiatanRepository(db).get(lamaran.mbkm_id)
    if not kegiatan.dimiliki_oleh(mitra.mitra_id):
        raise HTTPException(status_code=403, detail="Bukan lamaran untuk kegiatan Anda")

    # panggil method domain (yang punya business rule: tidak boleh ubah kalau sudah final)
    try:
        lamaran.ubah_status(data.status_pendaftaran)
    except ForbiddenActionError as e:
        raise HTTPException(status_code=400, detail=str(e))

    lamaran_repo.simpan_perubahan(lamaran)

    # buat notifikasi otomatis (ambil user_id dari mahasiswa)
    mhs = MahasiswaRepository(db).get(lamaran.mahasiswa_id)
    notif = Notifikasi(
        user_id=mhs.user_id,
        judul="Status Lamaran Diperbarui",
        pesan=(
            f"Lamaran Anda untuk '{kegiatan.nama_kegiatan}' "
            f"sekarang berstatus: {data.status_pendaftaran.value}."
        ),
        jenis_notifikasi=JenisNotifikasi.STATUS_LAMARAN,
    )
    notif_repo.buat(notif)
    lamaran_repo.commit()
    return lamaran