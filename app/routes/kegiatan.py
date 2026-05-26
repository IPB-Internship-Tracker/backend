from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_mitra, get_current_user
from app.domain.exceptions import ForbiddenActionError
from app.domain.kegiatan import (
    KategoriMBKM,
    KegiatanMBKM,
    Lomba,
    Magang,
    StatusKegiatan,
    StudiIndependen,
)
from app.domain.kegiatan_draft import KegiatanDraft
from app.domain.mitra import Mitra
from app.domain.user import User
from app.repositories import KegiatanDraftRepository, KegiatanRepository
from app.schemas import (
    KegiatanDraftCreate,
    KegiatanDraftResponse,
    KegiatanDraftUpdate,
    KegiatanResponse,
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

_LOMBA_STUDI_DB_DEFAULTS = {
    "kuota": 1,
    "syarat_ketentuan": "",
    "narahubung": "",
    "info_lebih_lanjut": "",
}


def _get_milik_mitra(
    repo: KegiatanRepository, mbkm_id: int, mitra: Mitra
) -> KegiatanMBKM:
    kegiatan = repo.get(mbkm_id)
    if kegiatan is None:
        raise HTTPException(status_code=404, detail="Kegiatan tidak ditemukan")
    if not kegiatan.dimiliki_oleh(mitra.mitra_id):  # method domain
        raise HTTPException(status_code=403, detail="Anda bukan pemilik kegiatan ini")
    return kegiatan


def _get_draft_milik_mitra(
    repo: KegiatanDraftRepository, draft_id: int, mitra: Mitra
) -> KegiatanDraft:
    draft = repo.get(draft_id)
    if draft is None:
        raise HTTPException(status_code=404, detail="Draft tidak ditemukan")
    if not draft.dimiliki_oleh(mitra.mitra_id):
        raise HTTPException(status_code=403, detail="Anda bukan pemilik draft ini")
    return draft


def _format_validation_errors(exc: ValidationError) -> list[dict]:
    errors = []
    for error in exc.errors():
        if "ctx" in error:
            error = {**error, "ctx": {key: str(value) for key, value in error["ctx"].items()}}
        errors.append(error)
    return errors


def _with_lomba_studi_defaults(data: dict) -> dict:
    return {**_LOMBA_STUDI_DB_DEFAULTS, **data}


def _kegiatan_response(kegiatan: KegiatanMBKM) -> dict:
    if isinstance(kegiatan, Magang):
        return MagangResponse.model_validate(kegiatan).model_dump()
    if isinstance(kegiatan, Lomba):
        return LombaResponse.model_validate(kegiatan).model_dump()
    if isinstance(kegiatan, StudiIndependen):
        return StudiIndependenResponse.model_validate(kegiatan).model_dump()
    raise HTTPException(status_code=500, detail="Tipe kegiatan tidak dikenali")


def _buat_kegiatan_dari_payload(
    kategori: KategoriMBKM, payload: dict, mitra: Mitra
) -> KegiatanMBKM:
    try:
        if kategori == KategoriMBKM.MAGANG:
            data = MagangCreate(**payload)
            data_dict = data.model_dump()
            data_dict["nama_perusahaan"] = data_dict["nama_perusahaan"] or mitra.nama_instansi
            return Magang(
                mitra_id=mitra.mitra_id,
                kategori_mbkm=KategoriMBKM.MAGANG,
                **data_dict,
            )
        if kategori == KategoriMBKM.LOMBA:
            data = LombaCreate(**payload)
            return Lomba(
                mitra_id=mitra.mitra_id,
                kategori_mbkm=KategoriMBKM.LOMBA,
                **_with_lomba_studi_defaults(data.model_dump()),
            )
        if kategori == KategoriMBKM.STUDI_INDEPENDEN:
            data = StudiIndependenCreate(**payload)
            return StudiIndependen(
                mitra_id=mitra.mitra_id,
                kategori_mbkm=KategoriMBKM.STUDI_INDEPENDEN,
                **_with_lomba_studi_defaults(data.model_dump()),
            )
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=_format_validation_errors(exc))

    raise HTTPException(status_code=400, detail="Kategori kegiatan tidak dikenali")


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
        **_with_lomba_studi_defaults(data.model_dump()),
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
        **_with_lomba_studi_defaults(data.model_dump()),
    )
    repo.buat(kegiatan)
    repo.commit()
    return kegiatan


# ---------- DRAFT ----------
@router.post("/draft", response_model=KegiatanDraftResponse, status_code=201)
def simpan_draft_kegiatan(
    data: KegiatanDraftCreate,
    mitra: Mitra = Depends(get_current_mitra),
    db: Session = Depends(get_db),
):
    repo = KegiatanDraftRepository(db)
    draft = KegiatanDraft(
        mitra_id=mitra.mitra_id,
        kategori_mbkm=data.kategori_mbkm,
        data=data.data,
    )
    draft = repo.buat(draft)
    repo.commit()
    return draft


@router.get("/draft/saya", response_model=list[KegiatanDraftResponse])
def list_draft_saya(
    mitra: Mitra = Depends(get_current_mitra),
    db: Session = Depends(get_db),
):
    return KegiatanDraftRepository(db).list_by_mitra(mitra.mitra_id)


@router.get("/draft/{draft_id}", response_model=KegiatanDraftResponse)
def detail_draft(
    draft_id: int,
    mitra: Mitra = Depends(get_current_mitra),
    db: Session = Depends(get_db),
):
    return _get_draft_milik_mitra(KegiatanDraftRepository(db), draft_id, mitra)


@router.patch("/draft/{draft_id}", response_model=KegiatanDraftResponse)
def update_draft(
    draft_id: int,
    data: KegiatanDraftUpdate,
    mitra: Mitra = Depends(get_current_mitra),
    db: Session = Depends(get_db),
):
    repo = KegiatanDraftRepository(db)
    draft = _get_draft_milik_mitra(repo, draft_id, mitra)
    draft.edit(kategori_mbkm=data.kategori_mbkm, data=data.data)
    draft = repo.simpan_perubahan(draft)
    repo.commit()
    return draft


@router.delete("/draft/{draft_id}", status_code=204)
def hapus_draft(
    draft_id: int,
    mitra: Mitra = Depends(get_current_mitra),
    db: Session = Depends(get_db),
):
    repo = KegiatanDraftRepository(db)
    draft = _get_draft_milik_mitra(repo, draft_id, mitra)
    draft.hapus()
    repo.hapus(draft_id)
    repo.commit()


@router.post("/draft/{draft_id}/publish", response_model=KegiatanResponse, status_code=201)
def publish_draft(
    draft_id: int,
    mitra: Mitra = Depends(get_current_mitra),
    db: Session = Depends(get_db),
):
    draft_repo = KegiatanDraftRepository(db)
    draft = _get_draft_milik_mitra(draft_repo, draft_id, mitra)
    kegiatan = _buat_kegiatan_dari_payload(draft.kategori_mbkm, draft.data, mitra)

    kegiatan_repo = KegiatanRepository(db)
    kegiatan_repo.buat(kegiatan)
    draft_repo.hapus(draft_id)
    kegiatan_repo.commit()
    return _kegiatan_response(kegiatan)


# ---------- READ ----------
@router.get("/", response_model=list[KegiatanResponse])
def list_kegiatan(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
    kategori: KategoriMBKM | None = None,
    status: StatusKegiatan | None = None,
    mitra_id: int | None = None,
):
    kegiatan_list = KegiatanRepository(db).list(
        kategori=kategori,
        status=status,
        mitra_id=mitra_id,
    )
    return [_kegiatan_response(kegiatan) for kegiatan in kegiatan_list]


@router.get("/{mbkm_id}", response_model=KegiatanResponse)
def detail_kegiatan(
    mbkm_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    kegiatan = KegiatanRepository(db).get(mbkm_id)
    if kegiatan is None:
        raise HTTPException(status_code=404, detail="Kegiatan tidak ditemukan")

    return _kegiatan_response(kegiatan)


# ---------- UPDATE ----------
def _apply_update(kegiatan: KegiatanMBKM, data_dict: dict) -> None:
    kegiatan.edit(**data_dict)


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
@router.post(
    "/{mbkm_id}/tutup-pendaftaran",
    response_model=KegiatanResponse,
    include_in_schema=False,
)
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
    return _kegiatan_response(kegiatan)


@router.delete("/{mbkm_id}", status_code=204)
def hapus_kegiatan(
    mbkm_id: int,
    mitra: Mitra = Depends(get_current_mitra),
    db: Session = Depends(get_db),
):
    repo = KegiatanRepository(db)
    kegiatan = _get_milik_mitra(repo, mbkm_id, mitra)  # pastikan milik
    try:
        kegiatan.hapus()
    except ForbiddenActionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    repo.hapus(mbkm_id)
    repo.commit()
