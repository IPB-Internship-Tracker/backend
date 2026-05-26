"""
Unit test untuk domain layer (pure Python, tanpa database).
Ini test paling cepat karena tidak butuh DB / FastAPI / HTTP.
"""
from datetime import date, timedelta

import pytest

from app.domain import (
    BidangMagang,
    DokumenLamaran,
    ForbiddenActionError,
    JenisNotifikasi,
    KategoriMBKM,
    Lamaran,
    Logbook,
    Lomba,
    Magang,
    Mahasiswa,
    Mitra,
    Notifikasi,
    PenempatanMagang,
    StatusKegiatan,
    StatusLamaran,
    StudiIndependen,
    TipeGaji,
    User,
    UserRole,
)

# User
class TestUser:
    def test_role_mahasiswa(self):
        u = User(nama="A", email="a@apps.ipb.ac.id",
                 password_hash="x", role=UserRole.MAHASISWA)
        assert u.is_mahasiswa() is True
        assert u.is_mitra() is False

    def test_role_mitra(self):
        u = User(nama="B", email="b@co.id",
                 password_hash="x", role=UserRole.MITRA)
        assert u.is_mitra() is True
        assert u.is_mahasiswa() is False

    def test_ganti_password(self):
        u = User(nama="X", email="x@x.com",
                 password_hash="lama", role=UserRole.MAHASISWA)
        u.ganti_password("baru")
        assert u.password_hash == "baru"

    def test_method_class_diagram_user(self):
        u = User(nama="X", email="x@x.com",
                 password_hash="hash123", role=UserRole.MAHASISWA)
        assert u.password == "hash123"
        assert u.login("x@x.com", "hash123") is True
        assert u.login("x@x.com", "salah") is False

        u.update_profil(nama="X Baru", email="XBARU@X.COM")
        assert u.nama == "X Baru"
        assert u.email == "xbaru@x.com"
        assert u.logout() is None


# =========================================================
# Mahasiswa / Mitra profile update
# =========================================================
class TestMahasiswaProfil:
    def test_mahasiswa_adalah_turunan_user(self):
        m = Mahasiswa(
            user_id=1,
            nama="Budi",
            email="budi@apps.ipb.ac.id",
            password_hash="hash123",
            nim="G6401231033",
            fakultas="Ilkom",
            program_studi="Ilkom",
        )
        assert isinstance(m, User)
        assert m.role == UserRole.MAHASISWA
        assert m.is_mahasiswa() is True
        assert m.login("budi@apps.ipb.ac.id", "hash123") is True

    def test_perbarui_nama_saja(self):
        m = Mahasiswa(user_id=1, nama="Budi", nim="G6401231033",
                      fakultas="Ilkom", program_studi="Ilkom")
        m.perbarui_profil(nama="Budi Baru")
        assert m.nama == "Budi Baru"
        assert m.program_studi == "Ilkom"  # tidak berubah
        assert m.foto_profile is None

    def test_perbarui_multi_field(self):
        m = Mahasiswa(user_id=1, nama="Budi", nim="A2024001001",
                      fakultas="Ilkom", program_studi="Ilkom")
        m.perbarui_profil(
            fakultas="FMIPA",
            program_studi="Statistika",
            foto_profile="https://example.com/budi.jpg",
        )
        assert m.fakultas == "FMIPA"
        assert m.program_studi == "Statistika"
        assert m.foto_profile == "https://example.com/budi.jpg"
        assert m.nama == "Budi"  # tetap

    def test_none_tidak_mengubah_apapun(self):
        m = Mahasiswa(user_id=1, nama="X", nim="B1999001234",
                      fakultas="F", program_studi="P")
        m.perbarui_profil(nama=None, semester=None)
        assert m.nama == "X"
        assert m.semester == 1

    def test_update_profil_alias(self):
        m = Mahasiswa(user_id=1, nama="X", nim="B1999001234",
                      fakultas="F", program_studi="P")
        m.update_profil(nama="X Baru")
        assert m.nama == "X Baru"


class TestMitraProfil:
    def test_mitra_adalah_turunan_user(self):
        mitra = Mitra(
            user_id=2,
            nama="HR PT A",
            email="hr@pta.co.id",
            password_hash="hash123",
            nama_instansi="PT A",
            jenis_instansi="Swasta",
            alamat="Jl. Lama",
            kontak="08111",
        )
        assert isinstance(mitra, User)
        assert mitra.role == UserRole.MITRA
        assert mitra.is_mitra() is True
        assert mitra.login("hr@pta.co.id", "hash123") is True

    def test_perbarui_alamat(self):
        mitra = Mitra(user_id=2, nama_instansi="PT A", jenis_instansi="Swasta",
                      alamat="Jl. Lama", kontak="08111")
        mitra.perbarui_profil(alamat="Jl. Baru")
        assert mitra.alamat == "Jl. Baru"
        assert mitra.nama_instansi == "PT A"

    def test_update_profil_alias(self):
        mitra = Mitra(user_id=2, nama_instansi="PT A", jenis_instansi="Swasta",
                      alamat="Jl. Lama", kontak="08111")
        mitra.update_profil(kontak="08222")
        assert mitra.kontak == "08222"


# =========================================================
# KegiatanMBKM state transition
# =========================================================
def _bikin_magang(status=StatusKegiatan.REGISTRASI_DIBUKA, deadline=None) -> Magang:
    return Magang(
        mitra_id=1, nama_kegiatan="Magang X", deskripsi="...",
        kategori_mbkm=KategoriMBKM.MAGANG,
        deadline_pendaftaran=deadline or (date.today() + timedelta(days=30)),
        kuota=5, tanggal_mulai=date.today() + timedelta(days=60),
        tanggal_selesai=date.today() + timedelta(days=120),
        syarat_ketentuan="IPK>3", status=status,
        narahubung="HR IPB",
        info_lebih_lanjut="https://example.com/magang",
        bidang=BidangMagang.INFORMATION_TECHNOLOGY,
        posisi="BE",
        nama_perusahaan="PT Testing",
        logo_url="https://example.com/logo.png",
        penempatan=PenempatanMagang.HYBRID,
        kota_lokasi="Bogor",
        alamat_lengkap="Jl. Testing No. 1",
        tipe_gaji=TipeGaji.PAID,
        gaji_perbulan=1_500_000,
        dokumen_dibutuhkan=[DokumenLamaran.CV, DokumenLamaran.TRANSKRIP_NILAI],
    )


class TestKegiatan:
    def test_default_status_dibuka(self):
        k = _bikin_magang()
        assert k.status == StatusKegiatan.REGISTRASI_DIBUKA
        assert k.is_pendaftaran_dibuka() is True
        assert k.status == "Registrasi Dibuka"

    def test_tutup_pendaftaran_menutup_status_manual(self):
        k = _bikin_magang(status=StatusKegiatan.REGISTRASI_DIBUKA)
        k.tutup_pendaftaran()
        assert k.status == StatusKegiatan.REGISTRASI_DITUTUP
        assert k.is_pendaftaran_dibuka() is False

    def test_status_manual_ditutup_tetap_dihormati(self):
        k = _bikin_magang(status=StatusKegiatan.REGISTRASI_DITUTUP)
        assert k.status == StatusKegiatan.REGISTRASI_DITUTUP
        assert k.is_pendaftaran_dibuka() is False

    def test_status_otomatis_ditutup_saat_deadline_lewat(self):
        k = _bikin_magang(deadline=date(2020, 1, 1))
        assert k.status == StatusKegiatan.REGISTRASI_DITUTUP
        assert k.is_pendaftaran_dibuka() is False
        assert k.status == "Registrasi Ditutup"

    def test_deadline_lewat(self):
        k_lewat = _bikin_magang(deadline=date(2020, 1, 1))
        k_belum = _bikin_magang(deadline=date(2099, 1, 1))
        assert k_lewat.is_deadline_lewat() is True
        assert k_belum.is_deadline_lewat() is False

    def test_deadline_lewat_dengan_tanggal_referensi(self):
        k = _bikin_magang(deadline=date(2025, 1, 1))
        assert k.is_deadline_lewat(hari_ini=date(2024, 12, 1)) is False
        assert k.is_deadline_lewat(hari_ini=date(2025, 6, 1)) is True

    def test_ownership(self):
        k = _bikin_magang()  # mitra_id=1
        assert k.dimiliki_oleh(1) is True
        assert k.dimiliki_oleh(99) is False

    def test_alias_dan_method_class_diagram(self):
        k = _bikin_magang()
        k.kegiatan_id = 10
        assert k.mbkm_id == 10
        assert k.kategori == KategoriMBKM.MAGANG
        assert k.info_lebihlanjut == k.info_lebih_lanjut
        assert k.tambah() is k

        k.edit(nama_kegiatan="Magang Baru", lokasi="Jakarta", uang_saku=2_000_000)
        assert k.nama_kegiatan == "Magang Baru"
        assert k.kota_lokasi == "Jakarta"
        assert k.gaji_perbulan == 2_000_000


# =========================================================
# Polymorfisme: Magang / Lomba / StudiIndependen
# =========================================================
class TestPolimorfismeKegiatan:
    @pytest.fixture
    def semua_jenis_kegiatan(self):
        today = date.today()
        deadline = today + timedelta(days=30)
        mulai = today + timedelta(days=60)
        selesai = today + timedelta(days=120)
        magang = Magang(
            mitra_id=1, nama_kegiatan="M", deskripsi=".",
            kategori_mbkm=KategoriMBKM.MAGANG,
            deadline_pendaftaran=deadline, kuota=1,
            tanggal_mulai=mulai, tanggal_selesai=selesai,
            syarat_ketentuan=".", narahubung="HR",
            info_lebih_lanjut="Info",
            bidang=BidangMagang.INFORMATION_TECHNOLOGY, posisi="BE",
            nama_perusahaan="PT Testing",
            penempatan=PenempatanMagang.WFO,
            kota_lokasi="Bogor", alamat_lengkap="Jl. Testing",
            tipe_gaji=TipeGaji.UNPAID, gaji_perbulan=0,
            dokumen_dibutuhkan=[DokumenLamaran.CV],
        )
        lomba = Lomba(
            mitra_id=1, nama_kegiatan="L", deskripsi=".",
            kategori_mbkm=KategoriMBKM.LOMBA,
            deadline_pendaftaran=deadline, kuota=1,
            tanggal_mulai=mulai, tanggal_selesai=selesai,
            syarat_ketentuan=".", narahubung="PIC",
            info_lebih_lanjut="Info", bidang=".", poster="poster.png",
        )
        studi = StudiIndependen(
            mitra_id=1, nama_kegiatan="S", deskripsi=".",
            kategori_mbkm=KategoriMBKM.STUDI_INDEPENDEN,
            deadline_pendaftaran=deadline, kuota=1,
            tanggal_mulai=mulai, tanggal_selesai=selesai,
            syarat_ketentuan=".", narahubung="PIC",
            info_lebih_lanjut="Info", bidang=".", poster="poster.png",
        )
        return [magang, lomba, studi]

    def test_semua_jenis_punya_method_parent(self, semua_jenis_kegiatan):
        for k in semua_jenis_kegiatan:
            assert k.is_pendaftaran_dibuka() is True
            assert k.dimiliki_oleh(1) is True
            assert isinstance(k.status, StatusKegiatan)


# =========================================================
# Lamaran — rule paling penting
# =========================================================
def _bikin_lamaran(status=StatusLamaran.TELAH_MENDAFTAR) -> Lamaran:
    return Lamaran(
        mahasiswa_id=1,
        mbkm_id=1,
        berkas_pendaftaran={DokumenLamaran.CV: "cv.pdf"},
        tanggal_daftar=date.today(), status_pendaftaran=status,
    )


class TestLamaran:
    def test_default_status(self):
        l = _bikin_lamaran()
        assert l.status_pendaftaran == StatusLamaran.TELAH_MENDAFTAR
        assert l.is_final() is False
        assert l.is_diterima() is False

    def test_transisi_valid(self):
        l = _bikin_lamaran()
        l.ubah_status(StatusLamaran.WAWANCARA)
        assert l.status_pendaftaran == StatusLamaran.WAWANCARA
        l.ubah_status(StatusLamaran.DITERIMA)
        assert l.is_diterima() is True
        assert l.is_final() is True

    @pytest.mark.parametrize("status_final", [
        StatusLamaran.DITERIMA,
        StatusLamaran.DITOLAK,
    ])
    def test_status_final_tidak_bisa_diubah(self, status_final):
        l = _bikin_lamaran(status=status_final)
        with pytest.raises(ForbiddenActionError, match="final"):
            l.ubah_status(StatusLamaran.WAWANCARA)

    def test_wawancara_bisa_diubah(self):
        l = _bikin_lamaran(status=StatusLamaran.WAWANCARA)
        l.ubah_status(StatusLamaran.DITERIMA)  # tidak raise
        assert l.is_diterima()

    def test_telah_mendaftar_bisa_diubah(self):
        l = _bikin_lamaran(status=StatusLamaran.TELAH_MENDAFTAR)
        l.ubah_status(StatusLamaran.DITOLAK)
        assert l.is_final()

    def test_method_class_diagram_lamaran(self):
        l = _bikin_lamaran()
        assert l.get_status() == StatusLamaran.TELAH_MENDAFTAR
        assert l.validate() is True

        l.tambah_berkas("portofolio.pdf")
        assert l.berkas_pendaftaran[DokumenLamaran.CV] == "portofolio.pdf"

        l.tambah_berkas(DokumenLamaran.PORTOFOLIO, "portfolio.pdf")
        assert l.berkas_pendaftaran[DokumenLamaran.PORTOFOLIO] == "portfolio.pdf"

        l.hapus_berkas()
        assert l.berkas_pendaftaran == {}
        assert l.validate() is False


# =========================================================
# Logbook — validasi __post_init__
# =========================================================
class TestLogbook:
    @pytest.mark.parametrize("durasi_invalid", [0, -10, 1441, 2000])
    def test_durasi_invalid(self, durasi_invalid):
        with pytest.raises(ForbiddenActionError, match="Durasi"):
            Logbook(lamaran_id=1, aktivitas="x",
                    durasi=durasi_invalid, tanggal=date.today())

    @pytest.mark.parametrize("durasi_valid", [1, 60, 480, 1440])
    def test_durasi_valid(self, durasi_valid):
        lb = Logbook(lamaran_id=1, aktivitas="Test",
                     durasi=durasi_valid, tanggal=date.today())
        assert lb.durasi == durasi_valid

    def test_alias_dan_method_class_diagram(self):
        lb = Logbook(lamaran_id=1, aktivitas="Test",
                     durasi=60, tanggal=date.today())
        assert lb.kegiatan_perhari == "Test"
        lb.kegiatan_perhari = "Meeting"
        assert lb.aktivitas == "Meeting"

        lb.edit(aktivitas="Coding", durasi=120)
        assert lb.aktivitas == "Coding"
        assert lb.durasi == 120
        assert lb.tambah_logbook() is lb
        assert lb.hapus() is lb


# =========================================================
# Notifikasi
# =========================================================
class TestNotifikasi:
    def test_default_belum_dibaca(self):
        n = Notifikasi(user_id=1, judul="X", pesan="Y",
                       jenis_notifikasi=JenisNotifikasi.STATUS_LAMARAN)
        assert n.status_baca is False

    def test_tandai_sudah_dibaca(self):
        n = Notifikasi(user_id=1, judul="X", pesan="Y",
                       jenis_notifikasi=JenisNotifikasi.STATUS_LAMARAN)
        n.tandai_sudah_dibaca()
        assert n.status_baca is True

    def test_tandai_sudah_dibaca_idempoten(self):
        """Memanggil tandai_sudah_dibaca pada yang sudah dibaca harus tetap True."""
        n = Notifikasi(user_id=1, judul="X", pesan="Y",
                       jenis_notifikasi=JenisNotifikasi.STATUS_LAMARAN,
                       status_baca=True)
        n.tandai_sudah_dibaca()
        assert n.status_baca is True

    def test_method_class_diagram_notifikasi(self):
        n = Notifikasi(user_id=1, judul="X", pesan="Y",
                       jenis_notifikasi=JenisNotifikasi.STATUS_LAMARAN)
        assert n.kirim_email() is False
        assert n.kirim_web() is True
