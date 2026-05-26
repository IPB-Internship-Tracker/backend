"""
Konfigurasi dan fixtures pytest untuk semua test.

Fixtures utama:
  - test_db          : membuat SQLite in-memory DB baru per test
  - client           : FastAPI TestClient yang pakai test_db
  - mahasiswa_token  : token JWT untuk mahasiswa sample
  - mitra_token      : token JWT untuk mitra sample
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import (  # noqa: F401 - pastikan semua tabel ter-register
    KegiatanMBKMORM,
    KegiatanDraftORM,
    LamaranORM,
    LogbookORM,
    MagangORM,
    MahasiswaORM,
    MitraORM,
    NotifikasiORM,
    UserORM,
)


TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_db():
    """
    Buat database SQLite in-memory baru untuk setiap test.
    Menggunakan StaticPool agar koneksi berbagi memory yang sama.
    """
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestingSessionLocal
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def client(test_db):
    """FastAPI TestClient yang otomatis pakai test_db."""
    with TestClient(app) as c:
        yield c


# ---------------- Helper untuk bikin user + login ----------------
MHS_PAYLOAD = {
    "nama": "Budi Testing",
    "email": "budi@apps.ipb.ac.id",
    "password": "rahasia123",
    "nim": "G6401231033",
    "fakultas": "Ilmu Komputer",
    "program_studi": "Ilmu Komputer",
}

MITRA_PAYLOAD = {
    "nama": "HR Testing",
    "email": "hr@testcorp.co.id",
    "password": "rahasia123",
    "nama_instansi": "PT Testing Corp",
    "jenis_instansi": "Swasta",
    "alamat": "Jl. Test No. 1, Bogor",
    "kontak": "081234567890",
}


def _register_and_login(client: TestClient, path: str, payload: dict) -> str:
    """Register + login, return access_token."""
    r = client.post(path, json=payload)
    assert r.status_code == 201, f"Register gagal: {r.text}"
    r = client.post(
        "/auth/login",
        data={"username": payload["email"], "password": payload["password"]},
    )
    assert r.status_code == 200, f"Login gagal: {r.text}"
    return r.json()["access_token"]


@pytest.fixture
def mahasiswa_token(client) -> str:
    """Register mahasiswa sample, return JWT token."""
    return _register_and_login(client, "/auth/register/mahasiswa", MHS_PAYLOAD)


@pytest.fixture
def mitra_token(client) -> str:
    """Register mitra sample, return JWT token."""
    return _register_and_login(client, "/auth/register/mitra", MITRA_PAYLOAD)


@pytest.fixture
def auth_header():
    """Helper untuk bikin header Authorization Bearer dari token."""
    def _make(token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}
    return _make


@pytest.fixture
def magang_kegiatan(client, mitra_token, auth_header) -> dict:
    """Bikin 1 kegiatan magang (sebagai mitra), return response body."""
    r = client.post(
        "/kegiatan/magang",
        json={
            "nama_kegiatan": "Magang Testing",
            "deskripsi": "Deskripsi panjang magang testing",
            "deadline_pendaftaran": "2099-06-01",
            "kuota": 5,
            "tanggal_mulai": "2099-07-01",
            "tanggal_selesai": "2099-09-01",
            "syarat_ketentuan": "IPK minimal 3.0",
            "narahubung": "HR Testing",
            "info_lebih_lanjut": "https://example.com/magang-testing",
            "bidang": "Information Technology",
            "posisi": "Backend Developer",
            "nama_perusahaan": "PT Testing Corp",
            "logo_url": "https://example.com/logo.png",
            "penempatan": "Hybrid",
            "kota_lokasi": "Bogor",
            "alamat_lengkap": "Jl. Test No. 1, Bogor",
            "tipe_gaji": "Paid",
            "gaji_perbulan": 2000000,
            "dokumen_dibutuhkan": ["Curriculum Vitae (CV)", "Transkrip Nilai"],
        },
        headers=auth_header(mitra_token),
    )
    assert r.status_code == 201, r.text
    return r.json()
