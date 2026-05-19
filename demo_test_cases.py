"""
DEMO TEST CASES — format naratif dengan contoh isian + hasil.

File ini dirancang untuk DITUNJUKKAN ke dosen/asisten.
Tiap test menampilkan: label, input yang diuji, hasil (OK/DITOLAK), dan pesan error.

Cara pakai:
    python demo_test_cases.py          # jalankan semua
    python -i demo_test_cases.py       # masuk interactive mode setelah demo

Berbeda dengan pytest (tests/), file ini lebih "mudah dibaca" untuk presentasi.
Untuk automated testing, pakai `pytest` di folder tests/.
"""
from datetime import date, timedelta
from pprint import pformat

from pydantic import ValidationError

# ==================== Domain layer ====================
from app.domain import (
    BidangMagang,
    DokumenLamaran,
    ForbiddenActionError,
    JenisNotifikasi,
    KategoriMBKM,
    Lamaran,
    Logbook,
    Magang,
    Mahasiswa,
    Mitra,
    Notifikasi,
    PenempatanMagang,
    StatusKegiatan,
    StatusLamaran,
    TipeGaji,
    User,
    UserRole,
)

# ==================== Schemas (Pydantic) ====================
from app.schemas import (
    LamaranCreate,
    LamaranStatusUpdate,
    LogbookCreate,
    MagangCreate,
    MahasiswaRegister,
    MitraRegister,
)

# ==================== Security ====================
from app.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


# ============================================================
#  Helper print
# ============================================================
def section(judul: str) -> None:
    print("\n" + "=" * 70)
    print(f"  {judul}")
    print("=" * 70)


def _format_input(isian: dict) -> str:
    """Format dict input jadi 1 baris pendek untuk di-print."""
    if len(isian) <= 3:
        return ", ".join(f"{k}={v!r}" for k, v in isian.items())
    # kalau field banyak, tampilkan multi-line
    return "\n       " + "\n       ".join(f"{k}={v!r}" for k, v in isian.items())


def coba_schema(label: str, SchemaClass, isian: dict, harus_valid: bool) -> None:
    """Coba bikin object schema, print label + input + hasil + error kalau ada."""
    status_hint = "HARUS VALID" if harus_valid else "HARUS DITOLAK"
    print(f"\n>> {label} ({status_hint})")
    print(f"   input: {_format_input(isian)}")
    try:
        obj = SchemaClass(**isian)
        if harus_valid:
            print("   [OK]")
            # tampilkan 1-2 field penting dari hasil
            data = obj.model_dump()
            penting = {k: v for k, v in data.items()
                       if k in ("email", "nim", "nama_instansi", "kuota",
                                "gaji_perbulan", "durasi", "status_pendaftaran",
                                "mbkm_id", "dokumen_dibutuhkan")}
            if penting:
                print(f"   hasil: {penting}")
        else:
            print("   [GAGAL] harusnya ditolak tapi object tetap dibuat")
    except ValidationError as e:
        if harus_valid:
            print("   [GAGAL] harusnya valid tapi ditolak:")
        else:
            print("   [DITOLAK]")
        for err in e.errors():
            loc = ".".join(str(x) for x in err["loc"])
            print(f"   - {loc}: {err['msg']}")


def coba_domain(label: str, fn, harus_raise: bool = False) -> None:
    """Coba jalankan fungsi domain, print hasilnya."""
    status_hint = "HARUS DITOLAK" if harus_raise else "HARUS VALID"
    print(f"\n>> {label} ({status_hint})")
    try:
        fn()
        if harus_raise:
            print("   [GAGAL] harusnya raise tapi jalan normal")
        else:
            print("   [OK]")
    except ForbiddenActionError as e:
        if harus_raise:
            print(f"   [DITOLAK oleh domain rule]")
            print(f"   - {e}")
        else:
            print(f"   [GAGAL] unexpected raise: {e}")


# ============================================================
# BAGIAN 1: VALIDASI SCHEMA PYDANTIC
# ============================================================
section("BAGIAN 1.A — Register mahasiswa (email harus @apps.ipb.ac.id)")

_mhs_valid_base = dict(
    nama="Budi Setiawan",
    password="rahasia123",
    nim="G64190001",
    fakultas="Ilmu Komputer",
    program_studi="Ilmu Komputer",
    angkatan=2023,
)

coba_schema("Email @apps.ipb.ac.id", MahasiswaRegister,
            {**_mhs_valid_base, "email": "budi@apps.ipb.ac.id"}, harus_valid=True)

coba_schema("Email @gmail.com", MahasiswaRegister,
            {**_mhs_valid_base, "email": "budi@gmail.com"}, harus_valid=False)

coba_schema("Email @yahoo.com", MahasiswaRegister,
            {**_mhs_valid_base, "email": "budi@yahoo.com"}, harus_valid=False)

coba_schema("Email @student.ipb.ac.id (bukan @apps.ipb.ac.id)", MahasiswaRegister,
            {**_mhs_valid_base, "email": "budi@student.ipb.ac.id"}, harus_valid=False)

coba_schema("Email kapital di-normalize ke lowercase", MahasiswaRegister,
            {**_mhs_valid_base, "email": "Budi@APPS.IPB.AC.ID"}, harus_valid=True)


section("BAGIAN 1.B — Validasi NIM")

coba_schema("NIM huruf+angka", MahasiswaRegister,
            {**_mhs_valid_base, "email": "a@apps.ipb.ac.id", "nim": "G64190999"}, harus_valid=True)

coba_schema("NIM dengan karakter '@'", MahasiswaRegister,
            {**_mhs_valid_base, "email": "a@apps.ipb.ac.id", "nim": "G6419@001"}, harus_valid=False)

coba_schema("NIM dengan spasi", MahasiswaRegister,
            {**_mhs_valid_base, "email": "a@apps.ipb.ac.id", "nim": "G 641 9001"}, harus_valid=False)

coba_schema("NIM dengan tanda hubung", MahasiswaRegister,
            {**_mhs_valid_base, "email": "a@apps.ipb.ac.id", "nim": "G64-190001"}, harus_valid=False)


section("BAGIAN 1.C — Password")

coba_schema("Password 8 karakter (minimum)", MahasiswaRegister,
            {**_mhs_valid_base, "email": "a@apps.ipb.ac.id", "password": "12345678"}, harus_valid=True)

coba_schema("Password hanya 3 karakter 'abc'", MahasiswaRegister,
            {**_mhs_valid_base, "email": "a@apps.ipb.ac.id", "password": "abc"}, harus_valid=False)

coba_schema("Password kosong ''", MahasiswaRegister,
            {**_mhs_valid_base, "email": "a@apps.ipb.ac.id", "password": ""}, harus_valid=False)


section("BAGIAN 1.D — Register mitra (email perusahaan)")

_mitra_valid_base = dict(
    nama="HR Test",
    password="rahasia123",
    nama_instansi="PT Test Corp",
    jenis_instansi="Swasta",
    alamat="Jl. Sudirman No. 1",
    kontak="081234567890",
)

coba_schema("Email perusahaan @testcorp.co.id", MitraRegister,
            {**_mitra_valid_base, "email": "hr@testcorp.co.id"}, harus_valid=True)

coba_schema("Email @gmail.com (konsumer)", MitraRegister,
            {**_mitra_valid_base, "email": "hr@gmail.com"}, harus_valid=False)

coba_schema("Email @yahoo.com (konsumer)", MitraRegister,
            {**_mitra_valid_base, "email": "hr@yahoo.com"}, harus_valid=False)

coba_schema("Email @hotmail.com (konsumer)", MitraRegister,
            {**_mitra_valid_base, "email": "hr@hotmail.com"}, harus_valid=False)

coba_schema("Email @outlook.com (konsumer)", MitraRegister,
            {**_mitra_valid_base, "email": "hr@outlook.com"}, harus_valid=False)

coba_schema("Email @icloud.com (konsumer)", MitraRegister,
            {**_mitra_valid_base, "email": "hr@icloud.com"}, harus_valid=False)

coba_schema("Email @startup.id (perusahaan)", MitraRegister,
            {**_mitra_valid_base, "email": "contact@startup.id"}, harus_valid=True)


section("BAGIAN 1.E — Validasi tanggal Kegiatan Magang")

_magang_base = dict(
    nama_kegiatan="Magang Backend",
    deskripsi="Belajar FastAPI dari nol",
    kuota=5,
    syarat_ketentuan="IPK minimal 3.0",
    narahubung="HR Test",
    info_lebih_lanjut="https://example.com/magang",
    bidang="Information Technology",
    posisi="Backend Developer",
    nama_perusahaan="PT Test Corp",
    logo_url="https://example.com/logo.png",
    penempatan="Hybrid",
    kota_lokasi="Bogor",
    alamat_lengkap="Jl. Test No. 1, Bogor",
    tipe_gaji="Paid",
    gaji_perbulan=1_500_000,
    dokumen_dibutuhkan=["Curriculum Vitae (CV)", "Transkrip Nilai"],
)

coba_schema("Tanggal valid (deadline < mulai < selesai)", MagangCreate, {
    **_magang_base,
    "deadline_pendaftaran": date(2099, 6, 1),
    "tanggal_mulai": date(2099, 7, 1),
    "tanggal_selesai": date(2099, 9, 1),
}, harus_valid=True)

coba_schema("tanggal_selesai SEBELUM tanggal_mulai", MagangCreate, {
    **_magang_base,
    "deadline_pendaftaran": date(2099, 6, 1),
    "tanggal_mulai": date(2099, 9, 1),
    "tanggal_selesai": date(2099, 7, 1),
}, harus_valid=False)

coba_schema("deadline_pendaftaran SETELAH tanggal_mulai", MagangCreate, {
    **_magang_base,
    "deadline_pendaftaran": date(2099, 8, 1),
    "tanggal_mulai": date(2099, 7, 1),
    "tanggal_selesai": date(2099, 9, 1),
}, harus_valid=False)


section("BAGIAN 1.F — Kuota dan Gaji Per Bulan")

coba_schema("kuota=5 (valid)", MagangCreate, {
    **_magang_base, "kuota": 5,
    "deadline_pendaftaran": date(2099, 6, 1),
    "tanggal_mulai": date(2099, 7, 1),
    "tanggal_selesai": date(2099, 9, 1),
}, harus_valid=True)

coba_schema("kuota=0 (harus > 0)", MagangCreate, {
    **_magang_base, "kuota": 0,
    "deadline_pendaftaran": date(2099, 6, 1),
    "tanggal_mulai": date(2099, 7, 1),
    "tanggal_selesai": date(2099, 9, 1),
}, harus_valid=False)

coba_schema("kuota=-1 (negatif)", MagangCreate, {
    **_magang_base, "kuota": -1,
    "deadline_pendaftaran": date(2099, 6, 1),
    "tanggal_mulai": date(2099, 7, 1),
    "tanggal_selesai": date(2099, 9, 1),
}, harus_valid=False)

coba_schema("gaji_perbulan=0 (boleh, misal magang tanpa dibayar)", MagangCreate, {
    **_magang_base, "gaji_perbulan": 0,
    "deadline_pendaftaran": date(2099, 6, 1),
    "tanggal_mulai": date(2099, 7, 1),
    "tanggal_selesai": date(2099, 9, 1),
}, harus_valid=True)

coba_schema("gaji_perbulan=-100 (negatif)", MagangCreate, {
    **_magang_base, "gaji_perbulan": -100,
    "deadline_pendaftaran": date(2099, 6, 1),
    "tanggal_mulai": date(2099, 7, 1),
    "tanggal_selesai": date(2099, 9, 1),
}, harus_valid=False)


section("BAGIAN 1.G — Validasi Lamaran & Logbook")

coba_schema("Lamaran valid", LamaranCreate, {
    "mbkm_id": 1, "berkas_pendaftaran": "cv_budi.pdf",
}, harus_valid=True)

coba_schema("Lamaran mbkm_id=0", LamaranCreate, {
    "mbkm_id": 0, "berkas_pendaftaran": "cv.pdf",
}, harus_valid=False)

coba_schema("Status lamaran 'diterima' (enum valid)", LamaranStatusUpdate, {
    "status_pendaftaran": "diterima",
}, harus_valid=True)

coba_schema("Status lamaran 'xyz' (enum tidak ada)", LamaranStatusUpdate, {
    "status_pendaftaran": "xyz",
}, harus_valid=False)

coba_schema("Logbook durasi=480 menit (8 jam)", LogbookCreate, {
    "lamaran_id": 1, "aktivitas": "Meeting tim backend untuk standup",
    "durasi": 480, "tanggal": date(2099, 7, 2),
}, harus_valid=True)

coba_schema("Logbook durasi=0", LogbookCreate, {
    "lamaran_id": 1, "aktivitas": "Test", "durasi": 0, "tanggal": date(2099, 7, 2),
}, harus_valid=False)

coba_schema("Logbook durasi=1441 (>1440 / >24 jam)", LogbookCreate, {
    "lamaran_id": 1, "aktivitas": "Test", "durasi": 1441, "tanggal": date(2099, 7, 2),
}, harus_valid=False)


# ============================================================
# BAGIAN 2: DOMAIN RULES (business logic)
# ============================================================
section("BAGIAN 2.A — User role methods")

print(">> User dengan role mahasiswa -> is_mahasiswa()=True")
u1 = User(nama="A", email="a@apps.ipb.ac.id", password_hash="x", role=UserRole.MAHASISWA)
print(f"   input: role=UserRole.MAHASISWA")
print(f"   hasil: is_mahasiswa()={u1.is_mahasiswa()}, is_mitra()={u1.is_mitra()}, is_admin()={u1.is_admin()}")

print("\n>> User dengan role mitra -> is_mitra()=True")
u2 = User(nama="B", email="b@co.id", password_hash="x", role=UserRole.MITRA)
print(f"   input: role=UserRole.MITRA")
print(f"   hasil: is_mahasiswa()={u2.is_mahasiswa()}, is_mitra()={u2.is_mitra()}, is_admin()={u2.is_admin()}")

print("\n>> User.ganti_password() mengubah hash")
u3 = User(nama="X", email="x@x.com", password_hash="lama", role=UserRole.MAHASISWA)
print(f"   input: password_hash='lama', lalu panggil ganti_password('baru')")
u3.ganti_password("baru")
print(f"   hasil: password_hash sekarang = {u3.password_hash!r}")


section("BAGIAN 2.B — Mahasiswa.perbarui_profil() partial update")

print(">> Update nama & angkatan saja, field lain tidak berubah")
m = Mahasiswa(user_id=1, nama="Budi", nim="G001",
              fakultas="Ilkom", program_studi="Ilkom", angkatan=2022)
print(f"   input awal: nama='Budi', fakultas='Ilkom', angkatan=2022")
print(f"   panggil: perbarui_profil(nama='Budi Baru', angkatan=2023)")
m.perbarui_profil(nama="Budi Baru", angkatan=2023)
print(f"   hasil: nama='{m.nama}', fakultas='{m.fakultas}', angkatan={m.angkatan}")


section("BAGIAN 2.C — Kegiatan state transition (tutup_pendaftaran)")

def _new_magang(status=StatusKegiatan.DIBUKA) -> Magang:
    return Magang(
        mitra_id=1, nama_kegiatan="X", deskripsi=".",
        kategori_mbkm=KategoriMBKM.MAGANG,
        deadline_pendaftaran=date(2099, 6, 1), kuota=1,
        tanggal_mulai=date(2099, 7, 1), tanggal_selesai=date(2099, 9, 1),
        syarat_ketentuan=".", status_kegiatan=status,
        narahubung="HR",
        info_lebih_lanjut="Info",
        bidang=BidangMagang.INFORMATION_TECHNOLOGY,
        posisi="Backend Developer",
        nama_perusahaan="PT Test Corp",
        penempatan=PenempatanMagang.WFO,
        kota_lokasi="Bogor",
        alamat_lengkap="Jl. Test No. 1",
        tipe_gaji=TipeGaji.UNPAID,
        gaji_perbulan=0,
        dokumen_dibutuhkan=[DokumenLamaran.CV],
    )

def tutup_dari_dibuka():
    k = _new_magang(StatusKegiatan.DIBUKA)
    k.tutup_pendaftaran()
    assert k.status_kegiatan == StatusKegiatan.DITUTUP

coba_domain("Kegiatan status DIBUKA -> tutup_pendaftaran() OK",
            tutup_dari_dibuka, harus_raise=False)

def tutup_dari_selesai():
    k = _new_magang(StatusKegiatan.SELESAI)
    k.tutup_pendaftaran()

coba_domain("Kegiatan status SELESAI -> tutup_pendaftaran() DITOLAK",
            tutup_dari_selesai, harus_raise=True)


section("BAGIAN 2.D — Lamaran state transition (RULE PALING PENTING)")

def _new_lamaran(status) -> Lamaran:
    return Lamaran(mahasiswa_id=1, mbkm_id=1, berkas_pendaftaran="cv.pdf",
                   tanggal_daftar=date.today(), status_pendaftaran=status)

def transisi_valid_chain():
    l = _new_lamaran(StatusLamaran.TELAH_MENDAFTAR)
    l.ubah_status(StatusLamaran.WAWANCARA)
    l.ubah_status(StatusLamaran.DITERIMA)

coba_domain("TELAH_MENDAFTAR -> WAWANCARA -> DITERIMA (chain valid)",
            transisi_valid_chain, harus_raise=False)

def dari_diterima():
    l = _new_lamaran(StatusLamaran.DITERIMA)
    l.ubah_status(StatusLamaran.WAWANCARA)

coba_domain("DITERIMA -> WAWANCARA (DITERIMA = final, harus ditolak)",
            dari_diterima, harus_raise=True)

def dari_ditolak():
    l = _new_lamaran(StatusLamaran.DITOLAK)
    l.ubah_status(StatusLamaran.DITERIMA)

coba_domain("DITOLAK -> DITERIMA (DITOLAK = final, harus ditolak)",
            dari_ditolak, harus_raise=True)

section("BAGIAN 2.E — Logbook __post_init__ durasi check")

for durasi in [0, -5, 1441, 9999]:
    def coba(d=durasi):
        Logbook(lamaran_id=1, aktivitas="x", durasi=d, tanggal=date.today())
    coba_domain(f"Logbook durasi={durasi}", coba, harus_raise=True)

for durasi in [1, 60, 480, 1440]:
    def coba(d=durasi):
        Logbook(lamaran_id=1, aktivitas="x", durasi=d, tanggal=date.today())
    coba_domain(f"Logbook durasi={durasi}", coba, harus_raise=False)


# ============================================================
# BAGIAN 3: SECURITY (Password + JWT)
# ============================================================
section("BAGIAN 3.A — Password hashing dengan bcrypt")

pw = "rahasia123"
h1 = hash_password(pw)
h2 = hash_password(pw)
print(f">> Hash password '{pw}' dua kali — hash sengaja BEDA karena bcrypt pakai salt")
print(f"   hash ke-1: {h1}")
print(f"   hash ke-2: {h2}")
print(f"   panjang  : {len(h1)} char (khas bcrypt)")

print(f"\n>> verify_password('{pw}', hash1) -> harus True")
print(f"   hasil: {verify_password(pw, h1)}")

print(f"\n>> verify_password('salah', hash1) -> harus False")
print(f"   hasil: {verify_password('salah', h1)}")


section("BAGIAN 3.B — JWT access token")

token = create_access_token(user_id=42, role=UserRole.MAHASISWA)
print(f">> Buat token untuk user_id=42, role=mahasiswa")
print(f"   token (3 bagian dipisah titik):")
print(f"   {token}")

payload = decode_access_token(token)
print(f"\n>> Decode token -> dapat payload dict")
print(f"   payload: {payload}")

print(f"\n>> Token di-utak-atik (tambah 'XXX') -> ditolak")
try:
    decode_access_token(token + "XXX")
    print("   [GAGAL] harusnya ditolak")
except ValueError as e:
    print(f"   [DITOLAK] {e}")

print(f"\n>> Token dengan masa berlaku -1 detik -> expired")
token_exp = create_access_token(user_id=1, role=UserRole.MITRA,
                                 expires_delta=timedelta(seconds=-1))
try:
    decode_access_token(token_exp)
    print("   [GAGAL] harusnya ditolak")
except ValueError as e:
    print(f"   [DITOLAK] {e}")


# ============================================================
#  Ringkasan
# ============================================================
print("\n" + "=" * 70)
print("  SELESAI. Semua contoh test case beserta input sudah ditampilkan.")
print()
print("  Untuk automated testing (CI-friendly), pakai:")
print("      pytest")
print("=" * 70)
