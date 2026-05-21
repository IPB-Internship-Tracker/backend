from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.config import settings


DOCUMENT_EXTENSIONS = {".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def _safe_suffix(filename: str | None) -> str:
    suffix = Path(filename or "").suffix.lower()
    return suffix


def save_upload_file(
    file: UploadFile,
    *,
    subdir: str,
    allowed_extensions: set[str],
) -> str:
    suffix = _safe_suffix(file.filename)
    if suffix not in allowed_extensions:
        allowed = ", ".join(sorted(allowed_extensions))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipe file tidak didukung. Gunakan: {allowed}",
        )

    upload_root = Path(settings.upload_dir)
    target_dir = upload_root / subdir
    target_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid4().hex}{suffix}"
    target = target_dir / filename

    total_bytes = 0
    try:
        with target.open("wb") as output:
            while chunk := file.file.read(1024 * 1024):
                total_bytes += len(chunk)
                if total_bytes > settings.upload_max_bytes:
                    output.close()
                    target.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="Ukuran file terlalu besar",
                    )
                output.write(chunk)
    finally:
        file.file.close()

    relative = target.relative_to(upload_root).as_posix()
    return f"/uploads/{relative}"
