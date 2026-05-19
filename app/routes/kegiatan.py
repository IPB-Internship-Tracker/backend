from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_mitra
from app.domain.exceptions import ForbiddenActionError
from app.domain.kegiatan import (
    KategoriMBKM,
    KegiatanMBKM,
    Lomba,
    Magang,
    StatusKegiatan,
    StudiIndependen,
)
from app.domain.mitra import Mitra
from app.repositories import KegiatanRepository
from app.schemas import (
    KegiatanListResponse,
    LombaCreate,
    LombaResponse,
    LombaUpdate,
    MagangCreate,
    MagangResponse,
    MagangUpdate,
    StudiIndependenCreate,
    StudiIndependenResponse,
    StudiIndependenUpdate,
)


router = APIRouter(prefix="/kegiatan", tags=["kegiatan"])


def _get_milik_mitra(
    repo: KegiatanRepository, mbkm_id: int, mitra: Mitra
) -> KegiatanMBKM:
    kegiatan = repo.get(mbkm_id)
    if kegiatan is None:
        raise HTTPException(status_code=404, detail="Kegiatan tidak ditemukan")
    if not kegiatan.dimiliki_oleh(mitra.mitra_id):  # method domain
        raise HTTPException(status_code=403, detail="Anda bukan pemilik kegiatan ini")
    return kegiatan


# ---------- CREATE ----------
@router.post("/magang", response_model=MagangResponse, status_code=201)
def buat_magang(
    data: MagangCreate,
    mitra: Mitra = Depends(get_current_mitra),
    db: Session = Depends(get_db),
):
    repo = KegiatanRepository(db)
    payload = data.model_dump()
    payload["nama_perusahaan"] = payload["nama_perusahaan"] or mitra.nama_instansi
    kegiatan = Magang(
        mitra_id=mitra.mitra_id,
        kategori_mbkm=KategoriMBKM.MAGANG,
        **payload,
    )
    repo.buat(kegiatan)
    repo.commit()
    return kegiatan


@router.post("/lomba", response_model=LombaResponse, status_code=201)
def buat_lomba(
    data: LombaCreate,
    mitra: Mitra = Depends(get_current_mitra),
    db: Session = Depends(get_db),
):
    repo = KegiatanRepository(db)
    kegiatan = Lomba(
        mitra_id=mitra.mitra_id,
        kategori_mbkm=KategoriMBKM.LOMBA,
        **data.model_dump(),
    )
    repo.buat(kegiatan)
    repo.commit()
    return kegiatan


@router.post("/studi-independen", response_model=StudiIndependenResponse, status_code=201)
def buat_studi_independen(
    data: StudiIndependenCreate,
    mitra: Mitra = Depends(get_current_mitra),
    db: Session = Depends(get_db),
):
    repo = KegiatanRepository(db)
    kegiatan = StudiIndependen(
        mitra_id=mitra.mitra_id,
        kategori_mbkm=KategoriMBKM.STUDI_INDEPENDEN,
        **data.model_dump(),
    )
    repo.buat(kegiatan)
    repo.commit()
    return kegiatan


# ---------- READ ----------
@router.get("/", response_model=list[KegiatanListResponse])
def list_kegiatan(
    db: Session = Depends(get_db),
    kategori: KategoriMBKM | None = None,
    status_kegiatan: StatusKegiatan | None = None,
    mitra_id: int | None = None,
):
    return KegiatanRepository(db).list(
        kategori=kategori, status_kegiatan=status_kegiatan, mitra_id=mitra_id
    )


@router.get("/{mbkm_id}")
def detail_kegiatan(mbkm_id: int, db: Session = Depends(get_db)):
    kegiatan = KegiatanRepository(db).get(mbkm_id)
    if kegiatan is None:
        raise HTTPException(status_code=404, detail="Kegiatan tidak ditemukan")

    if isinstance(kegiatan, Magang):
        return MagangResponse.model_validate(kegiatan).model_dump()
    if isinstance(kegiatan, Lomba):
        return LombaResponse.model_validate(kegiatan).model_dump()
    if isinstance(kegiatan, StudiIndependen):
        return StudiIndependenResponse.model_validate(kegiatan).model_dump()
    return KegiatanListResponse.model_validate(kegiatan).model_dump()


# ---------- UPDATE ----------
def _apply_update(kegiatan: KegiatanMBKM, data_dict: dict) -> None:
    for field, value in data_dict.items():
        setattr(kegiatan, field, value)


@router.patch("/magang/{mbkm_id}", response_model=MagangResponse)
def update_magang(
    mbkm_id: int,
    data: MagangUpdate,
    mitra: Mitra = Depends(get_current_mitra),
    db: Session = Depends(get_db),
):
    repo = KegiatanRepository(db)
    kegiatan = _get_milik_mitra(repo, mbkm_id, mitra)
    if not isinstance(kegiatan, Magang):
        raise HTTPException(status_code=400, detail="Kegiatan ini bukan tipe Magang")
    _apply_update(kegiatan, data.model_dump(exclude_unset=True))
    repo.simpan_perubahan(kegiatan)
    repo.commit()
    return kegiatan


@router.patch("/lomba/{mbkm_id}", response_model=LombaResponse)
def update_lomba(
    mbkm_id: int,
    data: LombaUpdate,
    mitra: Mitra = Depends(get_current_mitra),
    db: Session = Depends(get_db),
):
    repo = KegiatanRepository(db)
    kegiatan = _get_milik_mitra(repo, mbkm_id, mitra)
    if not isinstance(kegiatan, Lomba):
        raise HTTPException(status_code=400, detail="Kegiatan ini bukan tipe Lomba")
    _apply_update(kegiatan, data.model_dump(exclude_unset=True))
    repo.simpan_perubahan(kegiatan)
    repo.commit()
    return kegiatan


@router.patch("/studi-independen/{mbkm_id}", response_model=StudiIndependenResponse)
def update_studi_independen(
    mbkm_id: int,
    data: StudiIndependenUpdate,
    mitra: Mitra = Depends(get_current_mitra),
    db: Session = Depends(get_db),
):
    repo = KegiatanRepository(db)
    kegiatan = _get_milik_mitra(repo, mbkm_id, mitra)
    if not isinstance(kegiatan, StudiIndependen):
        raise HTTPException(status_code=400, detail="Kegiatan ini bukan tipe Studi Independen")
    _apply_update(kegiatan, data.model_dump(exclude_unset=True))
    repo.simpan_perubahan(kegiatan)
    repo.commit()
    return kegiatan


# ---------- ACTIONS ----------
@router.post("/{mbkm_id}/tutup-pendaftaran", response_model=KegiatanListResponse)
def tutup_pendaftaran(
    mbkm_id: int,
    mitra: Mitra = Depends(get_current_mitra),
    db: Session = Depends(get_db),
):
    repo = KegiatanRepository(db)
    kegiatan = _get_milik_mitra(repo, mbkm_id, mitra)
    try:
        kegiatan.tutup_pendaftaran()  # method domain dengan rule bisnis
    except ForbiddenActionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    repo.simpan_perubahan(kegiatan)
    repo.commit()
    return kegiatan


@router.delete("/{mbkm_id}", status_code=204)
def hapus_kegiatan(
    mbkm_id: int,
    mitra: Mitra = Depends(get_current_mitra),
    db: Session = Depends(get_db),
):
    repo = KegiatanRepository(db)
    _get_milik_mitra(repo, mbkm_id, mitra)  # pastikan milik
    repo.hapus(mbkm_id)
    repo.commit()
