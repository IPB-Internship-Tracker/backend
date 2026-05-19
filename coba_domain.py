"""
Demo manual untuk DOMAIN LAYER (pure Python, tanpa database).

Cara pakai:
    python coba_domain.py              # jalankan semua contoh
    python -i coba_domain.py           # lalu masuk interactive mode

Poin penting: script ini TIDAK butuh PostgreSQL jalan — karena domain layer
memang dirancang untuk bisa di-test tanpa infrastruktur.
"""
from datetime import date, timedelta

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


def section(judul: str) -> None:
    print("\n" + "=" * 60)
    print(f"  {judul}")
    print("=" * 60)


def coba(label: str, fn) -> None:
    """Coba jalankan, laporkan OK atau DITOLAK."""
    print(f"\n>> {label}")
    try:
        fn()
        print("   [OK]")
    except ForbiddenActionError as e:
        print(f"   [DITOLAK oleh domain rule] {e}")
    except AssertionError as e:
        print(f"   [ASSERTION GAGAL] {e}")


# =========================================================
# 1. USER — role check
# =========================================================
section("User — role check methods")

def test_user_roles():
    u_mhs = User(nama="A", email="a@apps.ipb.ac.id", password_hash="x", role=UserRole.MAHASISWA)
    u_mitra = User(nama="B", email="b@co.id", password_hash="x", role=UserRole.MITRA)
    u_admin = User(nama="C", email="c@x.com", password_hash="x", role=UserRole.ADMIN)

    assert u_mhs.is_mahasiswa() and not u_mhs.is_mitra()
    assert u_mitra.is_mitra() and not u_mitra.is_mahasiswa()
    assert u_admin.is_admin()
    print("   mahasiswa.is_mahasiswa() =", u_mhs.is_mahasiswa())
    print("   mitra.is_mitra()         =", u_mitra.is_mitra())
    print("   admin.is_admin()         =", u_admin.is_admin())

coba("User dengan role berbeda kasih jawaban is_* yang benar", test_user_roles)


def test_user_ganti_password():
    u = User(nama="X", email="x@x.com", password_hash="old_hash", role=UserRole.MAHASISWA)
    u.ganti_password("new_hash")
    assert u.password_hash == "new_hash"
    print("   password_hash lama -> baru:", u.password_hash)

coba("User.ganti_password() mengubah hash", test_user_ganti_password)


# =========================================================
# 2. MAHASISWA / MITRA — update profil
# =========================================================
section("Mahasiswa & Mitra — perbarui_profil()")

def test_mahasiswa_update():
    m = Mahasiswa(user_id=1, nama="Budi", nim="G64123",
                  fakultas="Ilkom", program_studi="Ilkom", angkatan=2022)
    m.perbarui_profil(nama="Budi Baru", angkatan=2023)
    assert m.nama == "Budi Baru" and m.angkatan == 2023
    assert m.nim == "G64123"  # NIM tidak berubah (tidak di-pass)
    print(f"   sesudah update: nama={m.nama} angkatan={m.angkatan} nim={m.nim} (tidak berubah)")

coba("Mahasiswa.perbarui_profil(): partial update berhasil, field lain tidak terpengaruh",
     test_mahasiswa_update)


def test_mitra_update():
    mitra = Mitra(user_id=2, nama_instansi="PT A", jenis_instansi="Swasta",
                  alamat="Jl. Lama", kontak="08111")
    mitra.perbarui_profil(alamat="Jl. Baru")
    assert mitra.alamat == "Jl. Baru" and mitra.nama_instansi == "PT A"
    print(f"   sesudah update: alamat={mitra.alamat} nama_instansi={mitra.nama_instansi}")

coba("Mitra.perbarui_profil(): hanya alamat yang berubah", test_mitra_update)


# =========================================================
# 3. KEGIATAN — state transition
# =========================================================
section("KegiatanMBKM — tutup_pendaftaran, is_*, dimiliki_oleh")


def _bikin_magang(status=StatusKegiatan.DIBUKA, deadline=None) -> Magang:
    return Magang(
        mitra_id=1, nama_kegiatan="Magang X", deskripsi="...",
        kategori_mbkm=KategoriMBKM.MAGANG,
        deadline_pendaftaran=deadline or (date.today() + timedelta(days=30)),
        kuota=5, tanggal_mulai=date.today() + timedelta(days=60),
        tanggal_selesai=date.today() + timedelta(days=120),
        syarat_ketentuan="IPK>3", status_kegiatan=status,
        narahubung="HR IPB",
        info_lebih_lanjut="https://example.com/magang",
        bidang=BidangMagang.INFORMATION_TECHNOLOGY,
        posisi="Backend Developer",
        nama_perusahaan="PT Test Corp",
        logo_url="https://example.com/logo.png",
        penempatan=PenempatanMagang.HYBRID,
        kota_lokasi="Bogor",
        alamat_lengkap="Jl. Test No. 1",
        tipe_gaji=TipeGaji.PAID,
        gaji_perbulan=1_500_000,
        dokumen_dibutuhkan=[DokumenLamaran.CV, DokumenLamaran.TRANSKRIP_NILAI],
    )


def test_tutup_pendaftaran_ok():
    k = _bikin_magang(status=StatusKegiatan.DIBUKA)
    assert k.is_pendaftaran_dibuka()
    k.tutup_pendaftaran()
    assert k.status_kegiatan == StatusKegiatan.DITUTUP
    assert not k.is_pendaftaran_dibuka()
    print(f"   status sesudah tutup: {k.status_kegiatan.value}")

coba("Kegiatan DIBUKA -> tutup_pendaftaran() jadi DITUTUP", test_tutup_pendaftaran_ok)


def test_tutup_kegiatan_selesai_ditolak():
    k = _bikin_magang(status=StatusKegiatan.SELESAI)
    k.tutup_pendaftaran()  # HARUS raise

coba("Kegiatan SELESAI tidak bisa ditutup lagi (harus ditolak)",
     test_tutup_kegiatan_selesai_ditolak)


def test_is_deadline_lewat():
    k_lewat = _bikin_magang(deadline=date(2020, 1, 1))
    k_belum = _bikin_magang(deadline=date(2099, 1, 1))
    assert k_lewat.is_deadline_lewat() is True
    assert k_belum.is_deadline_lewat() is False
    print(f"   deadline 2020-01-01 lewat? {k_lewat.is_deadline_lewat()}")
    print(f"   deadline 2099-01-01 lewat? {k_belum.is_deadline_lewat()}")

coba("is_deadline_lewat() bekerja benar", test_is_deadline_lewat)


def test_ownership():
    k = _bikin_magang()
    assert k.dimiliki_oleh(1) is True
    assert k.dimiliki_oleh(99) is False
    print("   dimiliki_oleh(1)  =", k.dimiliki_oleh(1))
    print("   dimiliki_oleh(99) =", k.dimiliki_oleh(99))

coba("Ownership check dimiliki_oleh()", test_ownership)


# =========================================================
# 4. LAMARAN — state transition rule yang paling penting
# =========================================================
section("Lamaran — rule: status FINAL tidak bisa diubah lagi")


def _bikin_lamaran(status=StatusLamaran.TELAH_MENDAFTAR) -> Lamaran:
    return Lamaran(
        mahasiswa_id=1, mbkm_id=1, berkas_pendaftaran="cv.pdf",
        tanggal_daftar=date.today(), status_pendaftaran=status,
    )


def test_transisi_valid():
    l = _bikin_lamaran()
    l.ubah_status(StatusLamaran.WAWANCARA)
    l.ubah_status(StatusLamaran.DITERIMA)
    assert l.is_diterima()
    assert l.is_final()
    print(f"   status akhir: {l.status_pendaftaran.value}")

coba("TELAH_MENDAFTAR -> WAWANCARA -> DITERIMA (valid)", test_transisi_valid)


def test_ubah_setelah_diterima_ditolak():
    l = _bikin_lamaran(status=StatusLamaran.DITERIMA)
    l.ubah_status(StatusLamaran.WAWANCARA)  # HARUS raise

coba("DITERIMA -> WAWANCARA (HARUS DITOLAK karena sudah final)",
     test_ubah_setelah_diterima_ditolak)


def test_ubah_setelah_ditolak_ditolak():
    l = _bikin_lamaran(status=StatusLamaran.DITOLAK)
    l.ubah_status(StatusLamaran.DITERIMA)

coba("DITOLAK -> DITERIMA (HARUS DITOLAK)", test_ubah_setelah_ditolak_ditolak)


# =========================================================
# 5. LOGBOOK — validasi durasi di __post_init__
# =========================================================
section("Logbook — validasi durasi (harus 1..1440 menit)")


def test_logbook_durasi_0_ditolak():
    Logbook(lamaran_id=1, aktivitas="x", durasi=0, tanggal=date.today())

coba("Logbook durasi=0 (HARUS DITOLAK)", test_logbook_durasi_0_ditolak)


def test_logbook_durasi_minus_ditolak():
    Logbook(lamaran_id=1, aktivitas="x", durasi=-10, tanggal=date.today())

coba("Logbook durasi=-10 (HARUS DITOLAK)", test_logbook_durasi_minus_ditolak)


def test_logbook_durasi_1500_ditolak():
    Logbook(lamaran_id=1, aktivitas="x", durasi=1500, tanggal=date.today())

coba("Logbook durasi=1500 (> 1440, HARUS DITOLAK)",
     test_logbook_durasi_1500_ditolak)


def test_logbook_valid():
    lb = Logbook(lamaran_id=1, aktivitas="Meeting tim", durasi=60, tanggal=date.today())
    assert lb.durasi == 60
    print(f"   logbook dibuat durasi={lb.durasi} aktivitas={lb.aktivitas!r}")

coba("Logbook durasi=60 menit (VALID)", test_logbook_valid)


# =========================================================
# 6. NOTIFIKASI — mark as read
# =========================================================
section("Notifikasi — tandai_sudah_dibaca()")


def test_notifikasi_mark_read():
    n = Notifikasi(user_id=1, judul="Halo", pesan="Test",
                   jenis_notifikasi=JenisNotifikasi.STATUS_LAMARAN)
    assert n.status_baca is False
    n.tandai_sudah_dibaca()
    assert n.status_baca is True
    print(f"   sebelum: False | sesudah: {n.status_baca}")

coba("Notifikasi default status_baca=False, tandai_sudah_dibaca() jadi True",
     test_notifikasi_mark_read)


# =========================================================
# 7. POLIMORFISME — Magang, Lomba, StudiIndependen semua KegiatanMBKM
# =========================================================
section("Polimorfisme — Magang, Lomba, StudiIndependen semua punya method parent")


def test_polymorphism():
    magang = Magang(
        mitra_id=1, nama_kegiatan="M", deskripsi=".", kategori_mbkm=KategoriMBKM.MAGANG,
        deadline_pendaftaran=date(2099, 1, 1), kuota=1,
        tanggal_mulai=date(2099, 2, 1), tanggal_selesai=date(2099, 3, 1),
        syarat_ketentuan=".", narahubung="HR", info_lebih_lanjut="Info",
        bidang=BidangMagang.INFORMATION_TECHNOLOGY, posisi="Backend Developer",
        nama_perusahaan="PT Test Corp", penempatan=PenempatanMagang.WFO,
        kota_lokasi="Bogor", alamat_lengkap="Jl. Test No. 1",
        tipe_gaji=TipeGaji.UNPAID, gaji_perbulan=0,
        dokumen_dibutuhkan=[DokumenLamaran.CV],
    )
    lomba = Lomba(
        mitra_id=1, nama_kegiatan="L", deskripsi=".", kategori_mbkm=KategoriMBKM.LOMBA,
        deadline_pendaftaran=date(2099, 1, 1), kuota=1,
        tanggal_mulai=date(2099, 2, 1), tanggal_selesai=date(2099, 3, 1),
        syarat_ketentuan=".", narahubung="PIC", info_lebih_lanjut="Info",
        bidang=".", tingkat_lomba=".",
        jenis_peserta=".", jumlah_anggota=1, hadiah=".",
    )
    studi = StudiIndependen(
        mitra_id=1, nama_kegiatan="S", deskripsi=".", kategori_mbkm=KategoriMBKM.STUDI_INDEPENDEN,
        deadline_pendaftaran=date(2099, 1, 1), kuota=1,
        tanggal_mulai=date(2099, 2, 1), tanggal_selesai=date(2099, 3, 1),
        syarat_ketentuan=".", narahubung="PIC", info_lebih_lanjut="Info",
        kurikulum=".", metode_pembelajaran=".", benefit=".",
    )

    # Semua punya method dari parent KegiatanMBKM
    for k in (magang, lomba, studi):
        assert k.is_pendaftaran_dibuka()
        assert k.dimiliki_oleh(1)
        print(f"   {type(k).__name__}: is_pendaftaran_dibuka()={k.is_pendaftaran_dibuka()}, "
              f"dimiliki_oleh(1)={k.dimiliki_oleh(1)}")

coba("Magang/Lomba/StudiIndependen semua inherit method parent", test_polymorphism)


print("\n" + "=" * 60)
print("  SELESAI. Domain layer berhasil di-test TANPA database.")
print("  Ini salah satu keuntungan besar pemisahan domain/ORM:")
print("  unit test domain jadi super cepat (tidak perlu Postgres).")
print("=" * 60)
