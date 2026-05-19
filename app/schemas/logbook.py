from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class LogbookCreate(BaseModel):
    lamaran_id: int = Field(gt=0)
    aktivitas: str = Field(min_length=5)
    durasi: int = Field(gt=0, le=1440, description="durasi dalam menit (max 1 hari = 1440)")
    tanggal: date
    foto: str | None = Field(default=None, max_length=255)


class LogbookUpdate(BaseModel):
    aktivitas: str | None = Field(default=None, min_length=5)
    durasi: int | None = Field(default=None, gt=0, le=1440)
    tanggal: date | None = None
    foto: str | None = Field(default=None, max_length=255)


class LogbookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    logbook_id: int
    lamaran_id: int
    foto: str | None
    aktivitas: str
    durasi: int
    tanggal: date