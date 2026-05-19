"""
Script untuk mencoba schema secara manual.

Cara pakai:
    python coba_schema.py              # jalankan semua contoh
    python -i coba_schema.py           # jalankan lalu masuk interactive mode
                                         (bisa bikin object baru di terminal)

Silakan edit/tambah/ubah bagian di bawah untuk eksperimen sendiri.
"""
from datetime import date
from pprint import pprint

from pydantic import ValidationError

from app.schemas import (
    MahasiswaRegister,
    MitraRegister,
    MagangCreate,
    LombaCreate,
    StudiIndependenCreate,
    LamaranCreate,
    LamaranStatusUpdate,
    LogbookCreate,
)
from app.domain.lamaran import StatusLamaran


def section(judul: str) -> None:
    print("\n" + "=" * 60)
    print(f"  {judul}")
    print("=" * 60)


def coba(label: str, fn) -> None:
    """Coba bikin object, print hasilnya (sukses atau error)."""
    print(f"\n>> {label}")
    try:
        obj = fn()
        print("   [SUKSES]")
        pprint(obj.model_dump(), width=100, sort_dicts=False, indent=4)
    except ValidationError as e:
        print("   [DITOLAK]")
        for err in e.errors():
            loc = ".".join(str(x) for x in err["loc"])
            print(f"   - {loc}: {err['msg']}")


# =========================================================
# 1. MAHASISWA REGISTER
# =========================================================
section("MahasiswaRegister — validasi email @apps.ipb.ac.id + NIM")

coba("Email @gmail.com (HARUS DITOLAK)", lambda: MahasiswaRegister(
    nama="Budi", email="budi@gmail.com", password="rahasia123",
    nim="G64190001", fakultas="Ilkom", program_studi="Ilkom", angkatan=2023,
))

coba("NIM dengan karakter aneh 'G6419@001' (HARUS DITOLAK)", lambda: MahasiswaRegister(
    nama="Budi", email="budi@apps.ipb.ac.id", password="rahasia123",
    nim="G6419@001", fakultas="Ilkom", program_studi="Ilkom", angkatan=2023,
))

coba("Password terlalu pendek 'abc' (HARUS DITOLAK)", lambda: MahasiswaRegister(
    nama="Budi", email="budi@apps.ipb.ac.id", password="abc",
    nim="G64190001", fakultas="Ilkom", program_studi="Ilkom", angkatan=2023,
))

coba("Valid — email & nim di-normalize (email lowercase, nim uppercase)",
     lambda: MahasiswaRegister(
    nama="Aulia", email="Aulia@APPS.IPB.AC.ID", password="rahasia123",
    nim="g64190999", fakultas="Ilmu Komputer",
    program_studi="Ilmu Komputer", angkatan=2023,
))


# =========================================================
# 2. MITRA REGISTER
# =========================================================
section("MitraRegister — blokir email konsumer (gmail/yahoo/dll)")

coba("Email @gmail.com (HARUS DITOLAK)", lambda: MitraRegister(
    nama="HR ABC", email="hr@gmail.com", password="rahasia123",
    nama_instansi="PT ABC", jenis_instansi="Swasta",
    alamat="Jl. Raya No. 1", kontak="0812345678",
))

coba("Email @abc.co.id (VALID — domain perusahaan)", lambda: MitraRegister(
    nama="HR ABC", email="hr@abc.co.id", password="rahasia123",
    nama_instansi="PT ABC", jenis_instansi="Swasta",
    alamat="Jl. Raya No. 1", kontak="0812345678",
))


# =========================================================
# 3. KEGIATAN MAGANG — validasi tanggal
# =========================================================
section("MagangCreate — validasi deadline & tanggal mulai/selesai")

coba("tanggal_selesai SEBELUM tanggal_mulai (HARUS DITOLAK)", lambda: MagangCreate(
    nama_kegiatan="Magang Backend", deskripsi="Belajar FastAPI",
    deadline_pendaftaran=date(2025, 6, 1), kuota=5,
    tanggal_mulai=date(2025, 7, 1), tanggal_selesai=date(2025, 6, 15),
    syarat_ketentuan="IPK > 3.0",
    narahubung="HR Test", info_lebih_lanjut="https://example.com/magang",
    bidang="Information Technology", posisi="Backend Dev",
    penempatan="Hybrid", kota_lokasi="Bogor", alamat_lengkap="Jl. Test No. 1",
    tipe_gaji="Paid", gaji_perbulan=1_500_000,
    dokumen_dibutuhkan=["Curriculum Vitae (CV)"],
))

coba("deadline SETELAH tanggal_mulai (HARUS DITOLAK)", lambda: MagangCreate(
    nama_kegiatan="Magang Backend", deskripsi="Belajar FastAPI",
    deadline_pendaftaran=date(2025, 8, 1), kuota=5,
    tanggal_mulai=date(2025, 7, 1), tanggal_selesai=date(2025, 9, 1),
    syarat_ketentuan="IPK > 3.0",
    narahubung="HR Test", info_lebih_lanjut="https://example.com/magang",
    bidang="Information Technology", posisi="Backend Dev",
    penempatan="Hybrid", kota_lokasi="Bogor", alamat_lengkap="Jl. Test No. 1",
    tipe_gaji="Paid", gaji_perbulan=1_500_000,
    dokumen_dibutuhkan=["Curriculum Vitae (CV)"],
))

coba("kuota=0 (HARUS DITOLAK — harus > 0)", lambda: MagangCreate(
    nama_kegiatan="Magang Backend", deskripsi="Belajar FastAPI",
    deadline_pendaftaran=date(2025, 6, 1), kuota=0,
    tanggal_mulai=date(2025, 7, 1), tanggal_selesai=date(2025, 9, 1),
    syarat_ketentuan="IPK > 3.0",
    narahubung="HR Test", info_lebih_lanjut="https://example.com/magang",
    bidang="Information Technology", posisi="Backend Dev",
    penempatan="Hybrid", kota_lokasi="Bogor", alamat_lengkap="Jl. Test No. 1",
    tipe_gaji="Paid", gaji_perbulan=1_500_000,
    dokumen_dibutuhkan=["Curriculum Vitae (CV)"],
))

coba("Magang valid lengkap", lambda: MagangCreate(
    nama_kegiatan="Magang Backend", deskripsi="Belajar FastAPI dari nol",
    deadline_pendaftaran=date(2025, 6, 1), kuota=5,
    tanggal_mulai=date(2025, 7, 1), tanggal_selesai=date(2025, 9, 1),
    syarat_ketentuan="IPK minimal 3.0",
    narahubung="HR Test",
    info_lebih_lanjut="https://example.com/magang",
    bidang="Information Technology", posisi="Backend Developer",
    nama_perusahaan="PT Test Corp",
    logo_url="https://example.com/logo.png",
    penempatan="Hybrid",
    kota_lokasi="Bogor",
    alamat_lengkap="Jl. Test No. 1",
    tipe_gaji="Paid",
    gaji_perbulan=1_500_000,
    dokumen_dibutuhkan=["Curriculum Vitae (CV)", "Transkrip Nilai"],
))


# =========================================================
# 4. LAMARAN
# =========================================================
section("LamaranCreate & LamaranStatusUpdate")

coba("Lamaran valid",
     lambda: LamaranCreate(mbkm_id=1, berkas_pendaftaran="cv_budi.pdf"))

coba("Update status -> DITERIMA",
     lambda: LamaranStatusUpdate(status_pendaftaran=StatusLamaran.DITERIMA))

coba("Update status -> WAWANCARA",
     lambda: LamaranStatusUpdate(status_pendaftaran=StatusLamaran.WAWANCARA))

coba("Status asing 'LUPA_DAFTAR' (HARUS DITOLAK)",
     lambda: LamaranStatusUpdate(status_pendaftaran="LUPA_DAFTAR"))


# =========================================================
# 5. LOGBOOK
# =========================================================
section("LogbookCreate — durasi dalam menit")

coba("durasi=0 (HARUS DITOLAK)", lambda: LogbookCreate(
    lamaran_id=1, aktivitas="Meeting dengan tim", durasi=0, tanggal=date.today(),
))

coba("durasi > 1440 (HARUS DITOLAK — max 1 hari = 1440 menit)", lambda: LogbookCreate(
    lamaran_id=1, aktivitas="Begadang sampai pagi",
    durasi=2000, tanggal=date.today(),
))

coba("Logbook valid (durasi 480 menit = 8 jam)", lambda: LogbookCreate(
    lamaran_id=1, aktivitas="Mengerjakan fitur login dengan FastAPI",
    durasi=480, tanggal=date.today(), foto=None,
))


print("\n" + "=" * 60)
print("  SELESAI. Silakan edit file ini untuk mencoba kasus lain.")
print("  Tip: jalankan 'python -i coba_schema.py' untuk masuk")
print("       interactive mode setelah demo selesai.")
print("=" * 60)
