"""
End-to-end test lewat HTTP (butuh server FastAPI jalan).

Cara pakai:
    # Terminal 1 — jalankan server:
    uvicorn app.main:app --reload

    # Terminal 2 — jalankan test:
    python coba_e2e.py

Script ini simulasi workflow lengkap:
  1. Register mahasiswa + mitra
  2. Login masing-masing (dapat JWT)
  3. Mitra buat kegiatan magang
  4. Mahasiswa daftar ke kegiatan
  5. Mitra ubah status lamaran -> notifikasi otomatis terbuat
  6. Domain rule: ubah status final -> 400
  7. Mahasiswa tambah logbook
  8. Tutup pendaftaran
  9. Mahasiswa baru coba daftar ke kegiatan yang sudah ditutup -> 400
 10. Role-based access: mahasiswa akses endpoint mitra -> 403

Data dibuat dengan suffix random, jadi bisa di-run berkali-kali
tanpa bentrok "email sudah terdaftar".
"""
import json
import random
import urllib.error
import urllib.parse
import urllib.request

import os
BASE_URL = os.environ.get("E2E_BASE_URL", "http://127.0.0.1:8000")


def req(method: str, path: str, body=None, token: str | None = None, form: bool = False):
    """HTTP request helper. Return (status_code, response_body_dict)."""
    url = BASE_URL + path
    if form:
        data = urllib.parse.urlencode(body).encode()
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
    else:
        data = json.dumps(body).encode() if body is not None else None
        headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            raw = resp.read()
            return resp.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as e:
        raw = e.read()
        return e.code, (json.loads(raw) if raw else None)
    except urllib.error.URLError:
        print(f"\n!! TIDAK BISA KONEK KE {BASE_URL}")
        print("   Pastikan uvicorn sudah jalan di terminal lain:")
        print("       uvicorn app.main:app --reload\n")
        raise SystemExit(1)


def expect(label: str, actual_code: int, expected_code: int, body=None) -> None:
    """Assert status code, print laporan."""
    status_ok = actual_code == expected_code
    mark = "OK " if status_ok else "FAIL"
    print(f"  [{mark}] {label} -> {actual_code}", end="")
    if body and not status_ok:
        print(f" | body: {body}")
    else:
        print()
    if not status_ok:
        raise SystemExit(f"Test gagal: {label}")


def section(judul: str) -> None:
    print("\n" + "=" * 60)
    print(f"  {judul}")
    print("=" * 60)


# ====================================================================
#  MULAI TEST
# ====================================================================
suffix = random.randint(100_000, 999_999)
mhs_email = f"mhs{suffix}@apps.ipb.ac.id"
mitra_email = f"hr{suffix}@testcorp.co.id"

section("1. ROOT endpoint")
code, body = req("GET", "/")
expect("GET /", code, 200)
print(f"       response: {body}")


section("2. REGISTER mahasiswa")
code, body = req("POST", "/auth/register/mahasiswa", {
    "nama": "Test Mahasiswa", "email": mhs_email, "password": "rahasia123",
    "nim": f"G64{suffix}", "fakultas": "Ilkom",
    "program_studi": "Ilmu Komputer", "angkatan": 2023,
})
expect("Register mahasiswa baru", code, 201, body)
print(f"       mahasiswa_id: {body['mahasiswa_id']}, nim: {body['nim']}")

# Validasi: email gmail ditolak
code, body = req("POST", "/auth/register/mahasiswa", {
    "nama": "X", "email": f"x{suffix}@gmail.com", "password": "12345678",
    "nim": f"G{suffix}9", "fakultas": "Fak", "program_studi": "Prodi", "angkatan": 2023,
})
expect("Register mahasiswa dengan @gmail.com ditolak", code, 422)


section("3. REGISTER mitra")
code, body = req("POST", "/auth/register/mitra", {
    "nama": "HR Test", "email": mitra_email, "password": "rahasia123",
    "nama_instansi": "PT Test Corp", "jenis_instansi": "Swasta",
    "alamat": "Jl. Test", "kontak": f"08{suffix}",
})
expect("Register mitra baru", code, 201)
print(f"       mitra_id: {body['mitra_id']}")

# Validasi: gmail untuk mitra juga ditolak
code, body = req("POST", "/auth/register/mitra", {
    "nama": "X", "email": f"x{suffix}@gmail.com", "password": "12345678",
    "nama_instansi": "X", "jenis_instansi": "X", "alamat": "X", "kontak": "08",
})
expect("Register mitra dengan @gmail.com ditolak", code, 422)


section("4. LOGIN & dapat JWT")
code, body = req("POST", "/auth/login",
                 {"username": mhs_email, "password": "rahasia123"}, form=True)
expect("Login mahasiswa", code, 200)
mhs_token = body["access_token"]
print(f"       token mahasiswa (10 char awal): {mhs_token[:10]}... role={body['role']}")

code, body = req("POST", "/auth/login",
                 {"username": mitra_email, "password": "rahasia123"}, form=True)
expect("Login mitra", code, 200)
mitra_token = body["access_token"]

# Login password salah
code, body = req("POST", "/auth/login",
                 {"username": mhs_email, "password": "salah"}, form=True)
expect("Login dengan password salah", code, 401)


section("5. /auth/me — ambil profil dari JWT")
code, body = req("GET", "/auth/me", token=mhs_token)
expect("GET /auth/me (mahasiswa)", code, 200)
print(f"       email={body['email']} role={body['role']}")


section("6. ROLE-BASED ACCESS — mahasiswa ditolak 403 di endpoint mitra")
code, body = req("POST", "/kegiatan/magang", {
    "nama_kegiatan": "X", "deskripsi": "xxxxxxxxxxxx",
    "deadline_pendaftaran": "2099-06-01", "kuota": 5,
    "tanggal_mulai": "2099-07-01", "tanggal_selesai": "2099-09-01",
    "syarat_ketentuan": "ok ok",
    "narahubung": "HR",
    "info_lebih_lanjut": "Info",
    "bidang": "Information Technology",
    "posisi": "Backend Dev",
    "penempatan": "WFO",
    "kota_lokasi": "Bogor",
    "alamat_lengkap": "Jl. Test",
    "tipe_gaji": "Unpaid",
    "gaji_perbulan": 0,
    "dokumen_dibutuhkan": ["Curriculum Vitae (CV)"],
}, token=mhs_token)
expect("Mahasiswa POST /kegiatan/magang (harus 403)", code, 403)


section("7. MITRA buat kegiatan magang")
code, kegiatan = req("POST", "/kegiatan/magang", {
    "nama_kegiatan": "Magang E2E Test", "deskripsi": "Test lengkap flow",
    "deadline_pendaftaran": "2099-06-01", "kuota": 3,
    "tanggal_mulai": "2099-07-01", "tanggal_selesai": "2099-09-01",
    "syarat_ketentuan": "IPK > 3.0",
    "narahubung": "HR Test",
    "info_lebih_lanjut": "https://example.com/magang-e2e",
    "bidang": "Information Technology",
    "posisi": "Backend Dev",
    "nama_perusahaan": "PT Test Corp",
    "logo_url": "https://example.com/logo.png",
    "penempatan": "Hybrid",
    "kota_lokasi": "Bogor",
    "alamat_lengkap": "Jl. Test No. 1, Bogor",
    "tipe_gaji": "Paid",
    "gaji_perbulan": 2_000_000,
    "dokumen_dibutuhkan": ["Curriculum Vitae (CV)", "Transkrip Nilai"],
}, token=mitra_token)
expect("Mitra POST /kegiatan/magang", code, 201)
kegiatan_id = kegiatan["mbkm_id"]
print(f"       kegiatan id={kegiatan_id} status={kegiatan['status_kegiatan']}")


section("8. LIST kegiatan (public)")
code, body = req("GET", "/kegiatan/")
expect("GET /kegiatan/ (public)", code, 200)
print(f"       total kegiatan di sistem: {len(body)}")

code, body = req("GET", "/kegiatan/?kategori=magang")
expect("GET /kegiatan/?kategori=magang", code, 200)
print(f"       total magang: {len(body)}")


section("9. MAHASISWA daftar lamaran")
code, lamaran = req("POST", "/lamaran/", {
    "mbkm_id": kegiatan_id, "berkas_pendaftaran": "cv_test.pdf",
}, token=mhs_token)
expect("Mahasiswa POST /lamaran/", code, 201)
lamaran_id = lamaran["lamaran_id"]
print(f"       lamaran id={lamaran_id} status={lamaran['status_pendaftaran']}")

# Duplikat
code, body = req("POST", "/lamaran/", {
    "mbkm_id": kegiatan_id, "berkas_pendaftaran": "cv2.pdf",
}, token=mhs_token)
expect("Daftar duplikat (harus 409)", code, 409)


section("10. MITRA lihat lamaran ke kegiatannya")
code, body = req("GET", f"/lamaran/kegiatan/{kegiatan_id}", token=mitra_token)
expect(f"GET /lamaran/kegiatan/{kegiatan_id}", code, 200)
print(f"       jumlah lamaran: {len(body)}")


section("11. MITRA ubah status lamaran -> WAWANCARA")
code, body = req("PATCH", f"/lamaran/{lamaran_id}/status",
                 {"status_pendaftaran": "wawancara"}, token=mitra_token)
expect("PATCH /lamaran/{id}/status = wawancara", code, 200)
print(f"       status baru: {body['status_pendaftaran']}")


section("12. MITRA ubah status -> DITERIMA (bikin notifikasi)")
code, body = req("PATCH", f"/lamaran/{lamaran_id}/status",
                 {"status_pendaftaran": "diterima"}, token=mitra_token)
expect("PATCH status = diterima", code, 200)


section("13. DOMAIN RULE: status final tidak bisa diubah")
code, body = req("PATCH", f"/lamaran/{lamaran_id}/status",
                 {"status_pendaftaran": "ditolak"}, token=mitra_token)
expect("PATCH status final -> ditolak (HARUS 400 dari domain)", code, 400)
print(f"       pesan error: {body['detail']}")


section("14. NOTIFIKASI ada di mahasiswa")
code, notifs = req("GET", "/notifikasi/saya", token=mhs_token)
expect("GET /notifikasi/saya", code, 200)
print(f"       total notifikasi: {len(notifs)}")
for n in notifs:
    print(f"         - [{n['jenis_notifikasi']}] {n['judul']}")

code, body = req("GET", "/notifikasi/saya/count-belum-dibaca", token=mhs_token)
expect("Count belum dibaca", code, 200)
print(f"       belum dibaca: {body['jumlah']}")

code, body = req("POST", "/notifikasi/saya/baca-semua", token=mhs_token)
expect("Mark all as read", code, 204)

code, body = req("GET", "/notifikasi/saya/count-belum-dibaca", token=mhs_token)
expect("Count belum dibaca (setelah baca semua)", code, 200)
assert body["jumlah"] == 0, "harusnya 0 setelah baca-semua"
print(f"       belum dibaca sesudah: {body['jumlah']}")


section("15. MAHASISWA tambah logbook (setelah diterima)")
code, body = req("POST", "/logbook/", {
    "lamaran_id": lamaran_id,
    "aktivitas": "Onboarding di perusahaan, setup environment, belajar codebase",
    "durasi": 480, "tanggal": "2099-07-02",
}, token=mhs_token)
expect("POST /logbook/", code, 201)
logbook_id = body["logbook_id"]

# Domain validation: durasi > 1440 ditolak
code, body = req("POST", "/logbook/", {
    "lamaran_id": lamaran_id, "aktivitas": "xxx kerja lembur",
    "durasi": 2000, "tanggal": "2099-07-02",
}, token=mhs_token)
expect("Logbook durasi=2000 (harus 422 dari Pydantic)", code, 422)


section("16. MITRA tutup pendaftaran kegiatan")
code, body = req("POST", f"/kegiatan/{kegiatan_id}/tutup-pendaftaran", token=mitra_token)
expect("POST /kegiatan/{id}/tutup-pendaftaran", code, 200)
print(f"       status sekarang: {body['status_kegiatan']}")


section("17. DOMAIN RULE: tidak bisa daftar ke kegiatan yang ditutup")
# bikin mahasiswa kedua untuk test ini
suffix2 = random.randint(100_000, 999_999)
mhs2_email = f"mhs2{suffix2}@apps.ipb.ac.id"
req("POST", "/auth/register/mahasiswa", {
    "nama": "Test Mahasiswa 2", "email": mhs2_email, "password": "rahasia123",
    "nim": f"G64{suffix2}", "fakultas": "Ilkom",
    "program_studi": "Ilkom", "angkatan": 2023,
})
_, b = req("POST", "/auth/login", {"username": mhs2_email, "password": "rahasia123"}, form=True)
mhs2_token = b["access_token"]

code, body = req("POST", "/lamaran/", {
    "mbkm_id": kegiatan_id, "berkas_pendaftaran": "cv3.pdf",
}, token=mhs2_token)
expect("Daftar ke kegiatan DITUTUP (harus 400)", code, 400)
print(f"       pesan error: {body['detail']}")


section("18. CLEANUP - mitra hapus kegiatan test")
code, body = req("DELETE", f"/kegiatan/{kegiatan_id}", token=mitra_token)
expect(f"DELETE /kegiatan/{kegiatan_id}", code, 204)


print("\n" + "=" * 60)
print("  SEMUA TEST LULUS - backend DDD bekerja end-to-end")
print("=" * 60)
