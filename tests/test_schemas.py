"""
Unit test untuk Pydantic schemas.
Memastikan validasi input (email IPB, tanggal kegiatan, dll) bekerja.
"""
from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas import (
    LamaranCreate,
    LamaranStatusUpdate,
    LogbookCreate,
    LombaCreate,
    MagangCreate,
    MahasiswaRegister,
    MitraRegister,
    StudiIndependenCreate,
)
from app.domain.kegiatan import BidangMagang, DokumenLamaran, PenempatanMagang, TipeGaji
from app.domain.lamaran import StatusLamaran


# =========================================================
# MahasiswaRegister — email harus @apps.ipb.ac.id
# =========================================================
class TestMahasiswaRegister:
    VALID_DATA = dict(
        nama="Budi",
        email="budi@apps.ipb.ac.id",
        password="rahasia123",
        nim="G6401231033",
        fakultas="Ilmu Komputer",
        program_studi="Ilmu Komputer",
    )

    def test_valid(self):
        m = MahasiswaRegister(**self.VALID_DATA)
        assert m.email == "budi@apps.ipb.ac.id"
        assert m.nim == "G6401231033"
        assert not hasattr(m, "foto_profile")
        assert not hasattr(m, "angkatan")

    def test_email_lowercase_dan_nim_uppercase(self):
        data = {**self.VALID_DATA, "email": "Budi@APPS.IPB.AC.ID", "nim": "g6401231033"}
        m = MahasiswaRegister(**data)
        assert m.email == "budi@apps.ipb.ac.id"
        assert m.nim == "G6401231033"

    @pytest.mark.parametrize("email_invalid", [
        "budi@gmail.com",
        "budi@yahoo.com",
        "budi@student.ipb.ac.id",  # domain lain
        "budi@ipb.ac.id",           # kurang "apps"
        "budi@cs.apps.ipb.ac.id",   # subdomain tetap tidak boleh
        "budi@apps.ipb.ac.id.evil.com",
    ])
    def test_email_selain_apps_ipb_ditolak(self, email_invalid):
        data = {**self.VALID_DATA, "email": email_invalid}
        with pytest.raises(ValidationError, match="apps.ipb.ac.id"):
            MahasiswaRegister(**data)

    def test_password_terlalu_pendek(self):
        data = {**self.VALID_DATA, "password": "abc"}
        with pytest.raises(ValidationError):
            MahasiswaRegister(**data)

    def test_nim_dengan_karakter_spesial_ditolak(self):
        data = {**self.VALID_DATA, "nim": "G640123103@"}
        with pytest.raises(ValidationError, match="angka"):
            MahasiswaRegister(**data)


# =========================================================
# MitraRegister — email perusahaan, bukan konsumer
# =========================================================
class TestMitraRegister:
    VALID_DATA = dict(
        nama="HR Test",
        email="hr@testcorp.co.id",
        password="rahasia123",
        nama_instansi="PT Test Corp",
        jenis_instansi="Swasta",
        alamat="Jl. Test No. 1",
        kontak="081234567890",
    )

    def test_valid(self):
        m = MitraRegister(**self.VALID_DATA)
        assert m.email == "hr@testcorp.co.id"

    @pytest.mark.parametrize("email_konsumer", [
        "hr@gmail.com",
        "hr@yahoo.com",
        "hr@hotmail.com",
        "hr@outlook.com",
        "hr@icloud.com",
    ])
    def test_email_konsumer_ditolak(self, email_konsumer):
        data = {**self.VALID_DATA, "email": email_konsumer}
        with pytest.raises(ValidationError, match="perusahaan"):
            MitraRegister(**data)

    @pytest.mark.parametrize("email_perusahaan", [
        "hr@perusahaan.co.id",
        "contact@startup.id",
        "info@company.com",
    ])
    def test_email_perusahaan_diterima(self, email_perusahaan):
        data = {**self.VALID_DATA, "email": email_perusahaan}
        m = MitraRegister(**data)
        assert m.email == email_perusahaan


# =========================================================
# MagangCreate — validasi tanggal
# =========================================================
class TestMagangCreate:
    VALID_DATA = dict(
        nama_kegiatan="Magang Backend",
        deskripsi="Belajar FastAPI dari nol",
        deadline_pendaftaran=date(2099, 6, 1),
        kuota=5,
        tanggal_mulai=date(2099, 7, 1),
        tanggal_selesai=date(2099, 9, 1),
        syarat_ketentuan="IPK minimal 3.0",
        narahubung="HR Test",
        info_lebih_lanjut="https://example.com/magang-backend",
        bidang=BidangMagang.INFORMATION_TECHNOLOGY,
        posisi="Backend Developer",
        nama_perusahaan="PT Test Corp",
        logo_url="https://example.com/logo.png",
        penempatan=PenempatanMagang.HYBRID,
        kota_lokasi="Bogor",
        alamat_lengkap="Jl. Test No. 1, Bogor",
        tipe_gaji=TipeGaji.PAID,
        gaji_perbulan=1_500_000,
        dokumen_dibutuhkan=[DokumenLamaran.CV, DokumenLamaran.TRANSKRIP_NILAI],
    )

    def test_valid(self):
        m = MagangCreate(**self.VALID_DATA)
        assert m.gaji_perbulan == 1_500_000
        assert m.bidang == BidangMagang.INFORMATION_TECHNOLOGY

    def test_tanggal_selesai_sebelum_mulai_ditolak(self):
        data = {**self.VALID_DATA,
                "tanggal_mulai": date(2099, 8, 1),
                "tanggal_selesai": date(2099, 7, 1)}
        with pytest.raises(ValidationError, match="tanggal_selesai"):
            MagangCreate(**data)

    def test_deadline_setelah_tanggal_mulai_ditolak(self):
        data = {**self.VALID_DATA,
                "deadline_pendaftaran": date(2099, 8, 1),
                "tanggal_mulai": date(2099, 7, 1)}
        with pytest.raises(ValidationError, match="deadline_pendaftaran"):
            MagangCreate(**data)

    def test_kuota_0_ditolak(self):
        data = {**self.VALID_DATA, "kuota": 0}
        with pytest.raises(ValidationError):
            MagangCreate(**data)

    def test_kuota_negatif_ditolak(self):
        data = {**self.VALID_DATA, "kuota": -1}
        with pytest.raises(ValidationError):
            MagangCreate(**data)

    def test_gaji_perbulan_negatif_ditolak(self):
        data = {**self.VALID_DATA, "gaji_perbulan": -100}
        with pytest.raises(ValidationError):
            MagangCreate(**data)


class TestLombaCreate:
    VALID_DATA = dict(
        nama_kegiatan="Lomba UI UX",
        deskripsi="Kompetisi desain produk digital nasional",
        deadline_pendaftaran=date(2099, 6, 1),
        tanggal_mulai=date(2099, 7, 1),
        tanggal_selesai=date(2099, 7, 3),
        bidang="Desain",
        poster="https://example.com/poster-lomba.png",
    )

    def test_valid_tanpa_field_yang_tidak_dipakai(self):
        lomba = LombaCreate(**self.VALID_DATA)

        assert lomba.nama_kegiatan == "Lomba UI UX"
        assert lomba.bidang == "Desain"
        assert lomba.poster == "https://example.com/poster-lomba.png"
        assert not hasattr(lomba, "narahubung")
        assert not hasattr(lomba, "kuota")
        assert not hasattr(lomba, "syarat_ketentuan")
        assert not hasattr(lomba, "info_lebih_lanjut")
        assert not hasattr(lomba, "tingkat_lomba")
        assert not hasattr(lomba, "jenis_peserta")
        assert not hasattr(lomba, "jumlah_anggota")
        assert not hasattr(lomba, "hadiah")


class TestStudiIndependenCreate:
    VALID_DATA = dict(
        nama_kegiatan="Studi Independen Backend",
        deskripsi="Program belajar backend intensif",
        deadline_pendaftaran=date(2099, 6, 1),
        tanggal_mulai=date(2099, 7, 1),
        tanggal_selesai=date(2099, 9, 1),
        bidang="Backend",
        poster="https://example.com/poster-studi.png",
    )

    def test_valid_tanpa_field_yang_tidak_dipakai(self):
        studi = StudiIndependenCreate(**self.VALID_DATA)

        assert studi.nama_kegiatan == "Studi Independen Backend"
        assert studi.bidang == "Backend"
        assert studi.poster == "https://example.com/poster-studi.png"
        assert not hasattr(studi, "narahubung")
        assert not hasattr(studi, "kuota")
        assert not hasattr(studi, "syarat_ketentuan")
        assert not hasattr(studi, "info_lebih_lanjut")
        assert not hasattr(studi, "kurikulum")
        assert not hasattr(studi, "metode_pembelajaran")
        assert not hasattr(studi, "benefit")


# =========================================================
# Lamaran schemas
# =========================================================
class TestLamaranSchemas:
    def test_lamaran_create_valid(self):
        l = LamaranCreate(
            mbkm_id=1,
            berkas_pendaftaran={"Curriculum Vitae (CV)": "cv.pdf"},
        )
        assert l.mbkm_id == 1
        assert l.berkas_pendaftaran[DokumenLamaran.CV] == "cv.pdf"

    def test_lamaran_create_mbkm_id_0_ditolak(self):
        with pytest.raises(ValidationError):
            LamaranCreate(
                mbkm_id=0,
                berkas_pendaftaran={"Curriculum Vitae (CV)": "cv.pdf"},
            )

    def test_lamaran_create_berkas_kosong_ditolak(self):
        with pytest.raises(ValidationError, match="tidak boleh kosong"):
            LamaranCreate(
                mbkm_id=1,
                berkas_pendaftaran={"Curriculum Vitae (CV)": ""},
            )

    @pytest.mark.parametrize("status", list(StatusLamaran))
    def test_status_update_semua_enum_valid(self, status):
        s = LamaranStatusUpdate(status_pendaftaran=status)
        assert s.status_pendaftaran == status

    def test_status_update_string_asing_ditolak(self):
        with pytest.raises(ValidationError):
            LamaranStatusUpdate(status_pendaftaran="status_tidak_ada")


# =========================================================
# Logbook schemas
# =========================================================
class TestLogbookSchemas:
    def test_valid(self):
        lb = LogbookCreate(
            lamaran_id=1, aktivitas="Meeting tim backend",
            durasi=60, tanggal=date(2099, 7, 2),
        )
        assert lb.durasi == 60

    @pytest.mark.parametrize("durasi_invalid", [0, -10, 1441, 2000])
    def test_durasi_invalid(self, durasi_invalid):
        with pytest.raises(ValidationError):
            LogbookCreate(
                lamaran_id=1, aktivitas="Test",
                durasi=durasi_invalid, tanggal=date.today(),
            )
