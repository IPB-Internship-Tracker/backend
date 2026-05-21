from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_mahasiswa
from app.domain.exceptions import ForbiddenActionError
from app.domain.lamaran import StatusLamaran
from app.domain.logbook import Logbook
from app.domain.mahasiswa import Mahasiswa
from app.repositories import LamaranRepository, LogbookRepository
from app.schemas import LogbookCreate, LogbookResponse, LogbookUpdate
from app.uploads import IMAGE_EXTENSIONS, save_upload_file


router = APIRouter(prefix="/logbook", tags=["logbook"])


def _ambil_logbook_saya(
    repo: LogbookRepository,
    lamaran_repo: LamaranRepository,
    logbook_id: int,
    mahasiswa: Mahasiswa,
) -> Logbook:
    logbook = repo.get(logbook_id)
    if logbook is None:
        raise HTTPException(status_code=404, detail="Logbook tidak ditemukan")
    lamaran = lamaran_repo.get(logbook.lamaran_id)
    if lamaran is None or lamaran.mahasiswa_id != mahasiswa.mahasiswa_id:
        raise HTTPException(status_code=403, detail="Bukan logbook Anda")
    return logbook


@router.post("/", response_model=LogbookResponse, status_code=201)
def tambah_logbook(
    data: LogbookCreate,
    mahasiswa: Mahasiswa = Depends(get_current_mahasiswa),
    db: Session = Depends(get_db),
):
    lamaran_repo = LamaranRepository(db)
    logbook_repo = LogbookRepository(db)

    lamaran = lamaran_repo.get(data.lamaran_id)
    if lamaran is None:
        raise HTTPException(status_code=404, detail="Lamaran tidak ditemukan")
    if lamaran.mahasiswa_id != mahasiswa.mahasiswa_id:
        raise HTTPException(status_code=403, detail="Bukan lamaran Anda")
    if lamaran.status_pendaftaran != StatusLamaran.DITERIMA:
        raise HTTPException(
            status_code=400,
            detail="Logbook hanya bisa diisi untuk lamaran yang sudah DITERIMA",
        )

    try:
        logbook = Logbook(**data.model_dump())  # bisa raise ForbiddenActionError
    except ForbiddenActionError as e:
        raise HTTPException(status_code=400, detail=str(e))

    logbook_repo.buat(logbook)
    logbook_repo.commit()
    return logbook


@router.post("/lamaran/{lamaran_id}/upload-foto")
def upload_foto_logbook(
    lamaran_id: int,
    file: UploadFile = File(...),
    mahasiswa: Mahasiswa = Depends(get_current_mahasiswa),
    db: Session = Depends(get_db),
) -> dict:
    lamaran = LamaranRepository(db).get(lamaran_id)
    if lamaran is None:
        raise HTTPException(status_code=404, detail="Lamaran tidak ditemukan")
    if lamaran.mahasiswa_id != mahasiswa.mahasiswa_id:
        raise HTTPException(status_code=403, detail="Bukan lamaran Anda")
    if lamaran.status_pendaftaran != StatusLamaran.DITERIMA:
        raise HTTPException(
            status_code=400,
            detail="Foto logbook hanya bisa diupload untuk lamaran yang sudah DITERIMA",
        )

    path = save_upload_file(
        file,
        subdir=f"logbook/mahasiswa-{mahasiswa.mahasiswa_id}/lamaran-{lamaran_id}",
        allowed_extensions=IMAGE_EXTENSIONS,
    )
    return {"foto": path, "path": path}


@router.get("/lamaran/{lamaran_id}", response_model=list[LogbookResponse])
def list_logbook(
    lamaran_id: int,
    mahasiswa: Mahasiswa = Depends(get_current_mahasiswa),
    db: Session = Depends(get_db),
):
    lamaran = LamaranRepository(db).get(lamaran_id)
    if lamaran is None:
        raise HTTPException(status_code=404, detail="Lamaran tidak ditemukan")
    if lamaran.mahasiswa_id != mahasiswa.mahasiswa_id:
        raise HTTPException(status_code=403, detail="Bukan lamaran Anda")
    return LogbookRepository(db).list_by_lamaran(lamaran_id)


@router.patch("/{logbook_id}", response_model=LogbookResponse)
def update_logbook(
    logbook_id: int,
    data: LogbookUpdate,
    mahasiswa: Mahasiswa = Depends(get_current_mahasiswa),
    db: Session = Depends(get_db),
):
    logbook_repo = LogbookRepository(db)
    logbook = _ambil_logbook_saya(logbook_repo, LamaranRepository(db), logbook_id, mahasiswa)
    logbook.edit(**data.model_dump(exclude_unset=True))
    logbook_repo.simpan_perubahan(logbook)
    logbook_repo.commit()
    return logbook


@router.delete("/{logbook_id}", status_code=204)
def hapus_logbook(
    logbook_id: int,
    mahasiswa: Mahasiswa = Depends(get_current_mahasiswa),
    db: Session = Depends(get_db),
):
    logbook_repo = LogbookRepository(db)
    _ambil_logbook_saya(logbook_repo, LamaranRepository(db), logbook_id, mahasiswa)
    logbook_repo.hapus(logbook_id)
    logbook_repo.commit()
