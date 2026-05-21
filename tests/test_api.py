"""
Integration test via FastAPI TestClient.
Test flow lengkap end-to-end tanpa butuh PostgreSQL (pakai SQLite in-memory).
"""
from datetime import date

import pytest

from app.security import create_password_reset_token
from app.domain.user import UserRole


def berkas_lamaran(cv: str = "cv.pdf", transkrip: str = "transkrip.pdf") -> dict:
    return {
        "Curriculum Vitae (CV)": cv,
        "Transkrip Nilai": transkrip,
    }


# =========================================================
# Root & Auth
# =========================================================
class TestRoot:
    def test_root(self, client):
        r = client.get("/")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ok"


class TestRegister:
    def test_register_mahasiswa(self, client):
        r = client.post("/auth/register/mahasiswa", json={
            "nama": "Budi", "email": "budi@apps.ipb.ac.id",
            "password": "rahasia123", "nim": "G6401231033",
            "fakultas": "Ilkom", "program_studi": "Ilkom", "angkatan": 2023,
            "semester": 3,
        })
        assert r.status_code == 201
        assert r.json()["nim"] == "G6401231033"
        assert r.json()["semester"] == 3

    def test_register_mahasiswa_email_gmail_ditolak(self, client):
        r = client.post("/auth/register/mahasiswa", json={
            "nama": "X", "email": "x@gmail.com", "password": "12345678",
            "nim": "A2024001001", "fakultas": "Ilkom", "program_studi": "Ilkom", "angkatan": 2023,
        })
        assert r.status_code == 422

    def test_register_email_duplikat_ditolak(self, client, mahasiswa_token):
        r = client.post("/auth/register/mahasiswa", json={
            "nama": "Lain", "email": "budi@apps.ipb.ac.id",  # sudah ada
            "password": "rahasia123", "nim": "B6402231034",
            "fakultas": "Ilkom", "program_studi": "Ilkom", "angkatan": 2023,
        })
        assert r.status_code == 409
        assert "Email sudah terdaftar" in r.json()["detail"]

    def test_register_nim_duplikat_ditolak(self, client, mahasiswa_token):
        r = client.post("/auth/register/mahasiswa", json={
            "nama": "Lain", "email": "lain@apps.ipb.ac.id",
            "password": "rahasia123", "nim": "G6401231033",  # sudah ada
            "fakultas": "Ilkom", "program_studi": "Ilkom", "angkatan": 2023,
        })
        assert r.status_code == 409
        assert "NIM sudah terdaftar" in r.json()["detail"]

    def test_register_mitra(self, client):
        r = client.post("/auth/register/mitra", json={
            "nama": "HR", "email": "hr@co.id", "password": "rahasia123",
            "nama_instansi": "PT A", "jenis_instansi": "Swasta",
            "alamat": "Jl. A No. 1", "kontak": "081234567",
        })
        assert r.status_code == 201


class TestLogin:
    def test_login_sukses(self, client, mahasiswa_token):
        # mahasiswa_token fixture sudah register + login, jadi token valid
        assert len(mahasiswa_token) > 20

    def test_login_password_salah(self, client, mahasiswa_token):
        r = client.post("/auth/login", data={
            "username": "budi@apps.ipb.ac.id", "password": "salah",
        })
        assert r.status_code == 401

    def test_login_user_tidak_ada(self, client):
        r = client.post("/auth/login", data={
            "username": "ghosts@apps.ipb.ac.id", "password": "rahasia123",
        })
        assert r.status_code == 401


class TestAuthMe:
    def test_get_me_dengan_token(self, client, mahasiswa_token, auth_header):
        r = client.get("/auth/me", headers=auth_header(mahasiswa_token))
        assert r.status_code == 200
        body = r.json()
        assert body["email"] == "budi@apps.ipb.ac.id"
        assert body["role"] == "mahasiswa"

    def test_get_me_tanpa_token_ditolak(self, client):
        r = client.get("/auth/me")
        assert r.status_code == 401

    def test_get_me_dengan_token_invalid(self, client, auth_header):
        r = client.get("/auth/me", headers=auth_header("xxx.invalid.token"))
        assert r.status_code == 401


class TestChangePassword:
    def test_ganti_password_sukses(self, client, mahasiswa_token, auth_header):
        r = client.post(
            "/auth/change-password",
            json={"password_lama": "rahasia123", "password_baru": "passwd123"},
            headers=auth_header(mahasiswa_token),
        )
        assert r.status_code == 204
        # login dengan password baru
        r = client.post("/auth/login", data={
            "username": "budi@apps.ipb.ac.id", "password": "passwd123",
        })
        assert r.status_code == 200

    def test_ganti_password_lama_salah(self, client, mahasiswa_token, auth_header):
        r = client.post(
            "/auth/change-password",
            json={"password_lama": "salah", "password_baru": "baru12345"},
            headers=auth_header(mahasiswa_token),
        )
        assert r.status_code == 400


class TestForgotPassword:
    def test_forgot_password_kirim_email_jika_user_ada(
        self, client, mahasiswa_token, monkeypatch,
    ):
        sent_emails = []

        def fake_send_notification_email(*, to_email: str, subject: str, message: str) -> bool:
            sent_emails.append({
                "to_email": to_email,
                "subject": subject,
                "message": message,
            })
            return True

        monkeypatch.setattr(
            "app.routes.auth.send_notification_email",
            fake_send_notification_email,
        )

        r = client.post("/auth/forgot-password", json={
            "email": "budi@apps.ipb.ac.id",
        })

        assert r.status_code == 200
        assert len(sent_emails) == 1
        assert sent_emails[0]["to_email"] == "budi@apps.ipb.ac.id"
        assert "Reset Password" in sent_emails[0]["subject"]
        assert "token=" in sent_emails[0]["message"]

    def test_forgot_password_email_tidak_terdaftar_tetap_200(self, client, monkeypatch):
        sent_emails = []

        def fake_send_notification_email(*, to_email: str, subject: str, message: str) -> bool:
            sent_emails.append(to_email)
            return True

        monkeypatch.setattr(
            "app.routes.auth.send_notification_email",
            fake_send_notification_email,
        )

        r = client.post("/auth/forgot-password", json={
            "email": "tidakada@apps.ipb.ac.id",
        })

        assert r.status_code == 200
        assert sent_emails == []

    def test_reset_password_sukses(self, client, mahasiswa_token):
        token = create_password_reset_token(
            user_id=1,
            role=UserRole.MAHASISWA,
        )

        r = client.post("/auth/reset-password", json={
            "token": token,
            "password_baru": "baru12345",
        })
        assert r.status_code == 204

        r = client.post("/auth/login", data={
            "username": "budi@apps.ipb.ac.id",
            "password": "baru12345",
        })
        assert r.status_code == 200

    def test_reset_password_token_invalid(self, client):
        r = client.post("/auth/reset-password", json={
            "token": "token.invalid",
            "password_baru": "baru12345",
        })
        assert r.status_code == 400


# =========================================================
# Role-based access control
# =========================================================
class TestRBAC:
    def test_mahasiswa_tidak_bisa_akses_endpoint_mitra(
        self, client, mahasiswa_token, auth_header,
    ):
        r = client.post("/kegiatan/magang", json={
            "nama_kegiatan": "X", "deskripsi": "xxxxxxxxxx",
            "deadline_pendaftaran": "2099-06-01", "kuota": 1,
            "tanggal_mulai": "2099-07-01", "tanggal_selesai": "2099-09-01",
            "syarat_ketentuan": "ok ok",
            "narahubung": "HR",
            "info_lebih_lanjut": "Info",
            "bidang": "Information Technology",
            "posisi": "Backend Developer",
            "penempatan": "WFO",
            "kota_lokasi": "Bogor",
            "alamat_lengkap": "Jl. Test",
            "tipe_gaji": "Unpaid",
            "gaji_perbulan": 0,
            "dokumen_dibutuhkan": ["Curriculum Vitae (CV)"],
        }, headers=auth_header(mahasiswa_token))
        assert r.status_code == 403
        assert "mitra" in r.json()["detail"].lower()

    def test_mitra_tidak_bisa_akses_endpoint_mahasiswa(
        self, client, mitra_token, auth_header,
    ):
        r = client.post("/lamaran/", json={
            "mbkm_id": 1, "berkas_pendaftaran": berkas_lamaran(),
        }, headers=auth_header(mitra_token))
        assert r.status_code == 403


# =========================================================
# Kegiatan CRUD
# =========================================================
class TestKegiatanCRUD:
    def test_mitra_buat_kegiatan_magang(self, client, magang_kegiatan):
        assert magang_kegiatan["nama_kegiatan"] == "Magang Testing"
        assert magang_kegiatan["kategori_mbkm"] == "magang"
        assert magang_kegiatan["status_kegiatan"] == "dibuka"

    def test_list_kegiatan_wajib_login(self, client, mahasiswa_token, magang_kegiatan, auth_header):
        r = client.get("/kegiatan/")
        assert r.status_code == 401

        r = client.get("/kegiatan/", headers=auth_header(mahasiswa_token))
        assert r.status_code == 200
        data = r.json()
        assert len(data) == 1
        assert data[0]["kategori_mbkm"] == "magang"

    def test_filter_kegiatan_by_kategori(self, client, mahasiswa_token, magang_kegiatan, auth_header):
        r = client.get("/kegiatan/?kategori=magang", headers=auth_header(mahasiswa_token))
        assert r.status_code == 200
        assert len(r.json()) == 1

        r = client.get("/kegiatan/?kategori=lomba", headers=auth_header(mahasiswa_token))
        assert r.status_code == 200
        assert len(r.json()) == 0

    def test_detail_kegiatan_magang_polymorphic(
        self, client, mahasiswa_token, magang_kegiatan, auth_header,
    ):
        r = client.get(f"/kegiatan/{magang_kegiatan['mbkm_id']}")
        assert r.status_code == 401

        r = client.get(
            f"/kegiatan/{magang_kegiatan['mbkm_id']}",
            headers=auth_header(mahasiswa_token),
        )
        assert r.status_code == 200
        body = r.json()
        # response harus punya field khusus magang
        assert body["bidang"] == "Information Technology"
        assert body["gaji_perbulan"] == 2_000_000
        assert body["narahubung"] == "HR Testing"

    def test_mitra_buat_lomba(self, client, mitra_token, auth_header):
        r = client.post("/kegiatan/lomba", json={
            "nama_kegiatan": "Lomba X", "deskripsi": "Lomba bergengsi",
            "deadline_pendaftaran": "2099-06-01", "kuota": 10,
            "tanggal_mulai": "2099-07-01", "tanggal_selesai": "2099-09-01",
            "syarat_ketentuan": "Mahasiswa aktif",
            "narahubung": "Panitia Lomba",
            "info_lebih_lanjut": "https://example.com/lomba",
            "bidang": "IT", "tingkat_lomba": "Nasional",
            "jenis_peserta": "Tim", "jumlah_anggota": 3,
            "hadiah": "Uang + sertifikat",
        }, headers=auth_header(mitra_token))
        assert r.status_code == 201
        assert r.json()["hadiah"] == "Uang + sertifikat"

    def test_tutup_pendaftaran(self, client, mitra_token, magang_kegiatan, auth_header):
        r = client.post(
            f"/kegiatan/{magang_kegiatan['mbkm_id']}/tutup-pendaftaran",
            headers=auth_header(mitra_token),
        )
        assert r.status_code == 200
        assert r.json()["status_kegiatan"] == "ditutup"

    def test_mitra_lain_tidak_bisa_tutup_kegiatan_orang_lain(
        self, client, magang_kegiatan, auth_header,
    ):
        # register + login mitra kedua
        client.post("/auth/register/mitra", json={
            "nama": "HR2", "email": "hr2@other.co.id", "password": "rahasia123",
            "nama_instansi": "PT Other", "jenis_instansi": "Swasta",
            "alamat": "Jl. Other", "kontak": "08198765432",
        })
        r = client.post("/auth/login",
                        data={"username": "hr2@other.co.id", "password": "rahasia123"})
        token2 = r.json()["access_token"]

        r = client.post(
            f"/kegiatan/{magang_kegiatan['mbkm_id']}/tutup-pendaftaran",
            headers=auth_header(token2),
        )
        assert r.status_code == 403

    def test_delete_kegiatan(self, client, mitra_token, magang_kegiatan, auth_header):
        r = client.delete(
            f"/kegiatan/{magang_kegiatan['mbkm_id']}",
            headers=auth_header(mitra_token),
        )
        assert r.status_code == 204
        r = client.get(
            f"/kegiatan/{magang_kegiatan['mbkm_id']}",
            headers=auth_header(mitra_token),
        )
        assert r.status_code == 404

    def test_mitra_bisa_simpan_update_dan_hapus_draft(
        self, client, mitra_token, auth_header,
    ):
        r = client.post(
            "/kegiatan/draft",
            json={
                "kategori_mbkm": "magang",
                "data": {
                    "nama_kegiatan": "Draft Magang",
                    "dokumen_dibutuhkan": ["Curriculum Vitae (CV)"],
                },
            },
            headers=auth_header(mitra_token),
        )
        assert r.status_code == 201, r.text
        draft = r.json()
        assert draft["kategori_mbkm"] == "magang"
        assert draft["data"]["nama_kegiatan"] == "Draft Magang"

        r = client.patch(
            f"/kegiatan/draft/{draft['draft_id']}",
            json={"data": {"posisi": "Backend Developer"}},
            headers=auth_header(mitra_token),
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["data"]["nama_kegiatan"] == "Draft Magang"
        assert body["data"]["posisi"] == "Backend Developer"

        r = client.get("/kegiatan/draft/saya", headers=auth_header(mitra_token))
        assert r.status_code == 200
        assert len(r.json()) == 1

        r = client.delete(
            f"/kegiatan/draft/{draft['draft_id']}",
            headers=auth_header(mitra_token),
        )
        assert r.status_code == 204

        r = client.get("/kegiatan/draft/saya", headers=auth_header(mitra_token))
        assert r.status_code == 200
        assert r.json() == []

    def test_publish_draft_magang_jadi_kegiatan(
        self, client, mitra_token, auth_header,
    ):
        payload = {
            "nama_kegiatan": "Magang Dari Draft",
            "deskripsi": "Deskripsi lengkap magang dari draft",
            "deadline_pendaftaran": "2099-06-01",
            "kuota": 5,
            "tanggal_mulai": "2099-07-01",
            "tanggal_selesai": "2099-09-01",
            "syarat_ketentuan": "IPK minimal 3.0",
            "narahubung": "HR Testing",
            "info_lebih_lanjut": "https://example.com/draft",
            "bidang": "Information Technology",
            "posisi": "Backend Developer",
            "penempatan": "Hybrid",
            "kota_lokasi": "Bogor",
            "alamat_lengkap": "Jl. Test No. 1, Bogor",
            "tipe_gaji": "Paid",
            "gaji_perbulan": 2000000,
            "dokumen_dibutuhkan": ["Curriculum Vitae (CV)", "Transkrip Nilai"],
        }
        r = client.post(
            "/kegiatan/draft",
            json={"kategori_mbkm": "magang", "data": payload},
            headers=auth_header(mitra_token),
        )
        assert r.status_code == 201, r.text
        draft_id = r.json()["draft_id"]

        r = client.post(
            f"/kegiatan/draft/{draft_id}/publish",
            headers=auth_header(mitra_token),
        )
        assert r.status_code == 201, r.text
        kegiatan = r.json()
        assert kegiatan["nama_kegiatan"] == "Magang Dari Draft"
        assert kegiatan["nama_perusahaan"] == "PT Testing Corp"
        assert kegiatan["kategori_mbkm"] == "magang"

        r = client.get("/kegiatan/draft/saya", headers=auth_header(mitra_token))
        assert r.status_code == 200
        assert r.json() == []

    def test_publish_draft_belum_lengkap_ditolak(
        self, client, mitra_token, auth_header,
    ):
        r = client.post(
            "/kegiatan/draft",
            json={
                "kategori_mbkm": "magang",
                "data": {"nama_kegiatan": "Belum Lengkap"},
            },
            headers=auth_header(mitra_token),
        )
        assert r.status_code == 201, r.text
        draft_id = r.json()["draft_id"]

        r = client.post(
            f"/kegiatan/draft/{draft_id}/publish",
            headers=auth_header(mitra_token),
        )
        assert r.status_code == 422

        r = client.get(f"/kegiatan/draft/{draft_id}", headers=auth_header(mitra_token))
        assert r.status_code == 200


# =========================================================
# Lamaran flow (tempat rule domain paling terlihat)
# =========================================================
class TestLamaranFlow:
    def test_mahasiswa_daftar_sukses(
        self, client, mahasiswa_token, magang_kegiatan, auth_header,
    ):
        r = client.post("/lamaran/", json={
            "mbkm_id": magang_kegiatan["mbkm_id"],
            "berkas_pendaftaran": berkas_lamaran(),
        }, headers=auth_header(mahasiswa_token))
        assert r.status_code == 201
        assert r.json()["status_pendaftaran"] == "telah_mendaftar"

    def test_mahasiswa_daftar_dokumen_wajib_belum_lengkap_ditolak(
        self, client, mahasiswa_token, magang_kegiatan, auth_header,
    ):
        r = client.post("/lamaran/", json={
            "mbkm_id": magang_kegiatan["mbkm_id"],
            "berkas_pendaftaran": {"Curriculum Vitae (CV)": "cv.pdf"},
        }, headers=auth_header(mahasiswa_token))
        assert r.status_code == 400
        assert "Transkrip Nilai" in r.json()["detail"]

    def test_upload_berkas_lamaran(self, client, mahasiswa_token, magang_kegiatan, auth_header, tmp_path, monkeypatch):
        monkeypatch.setattr("app.uploads.settings.upload_dir", str(tmp_path))
        r = client.post(
            f"/lamaran/{magang_kegiatan['mbkm_id']}/upload-berkas",
            data={"dokumen": "Curriculum Vitae (CV)"},
            files={"file": ("cv.pdf", b"isi cv", "application/pdf")},
            headers=auth_header(mahasiswa_token),
        )
        assert r.status_code == 200
        body = r.json()
        assert body["dokumen"] == "Curriculum Vitae (CV)"
        assert body["path"].startswith("/uploads/lamaran/")
        assert body["berkas_pendaftaran"]["Curriculum Vitae (CV)"] == body["path"]

    def test_daftar_ke_kegiatan_ga_ada_404(
        self, client, mahasiswa_token, auth_header,
    ):
        r = client.post("/lamaran/", json={
            "mbkm_id": 9999, "berkas_pendaftaran": berkas_lamaran(),
        }, headers=auth_header(mahasiswa_token))
        assert r.status_code == 404

    def test_daftar_duplikat_ditolak(
        self, client, mahasiswa_token, magang_kegiatan, auth_header,
    ):
        client.post("/lamaran/", json={
            "mbkm_id": magang_kegiatan["mbkm_id"],
            "berkas_pendaftaran": berkas_lamaran("cv1.pdf", "transkrip1.pdf"),
        }, headers=auth_header(mahasiswa_token))
        r = client.post("/lamaran/", json={
            "mbkm_id": magang_kegiatan["mbkm_id"],
            "berkas_pendaftaran": berkas_lamaran("cv2.pdf", "transkrip2.pdf"),
        }, headers=auth_header(mahasiswa_token))
        assert r.status_code == 409

    def test_daftar_ke_kegiatan_ditutup_ditolak(
        self, client, mahasiswa_token, mitra_token, magang_kegiatan, auth_header,
    ):
        # mitra tutup pendaftaran dulu
        client.post(
            f"/kegiatan/{magang_kegiatan['mbkm_id']}/tutup-pendaftaran",
            headers=auth_header(mitra_token),
        )
        # mahasiswa coba daftar
        r = client.post("/lamaran/", json={
            "mbkm_id": magang_kegiatan["mbkm_id"],
            "berkas_pendaftaran": berkas_lamaran(),
        }, headers=auth_header(mahasiswa_token))
        assert r.status_code == 400
        assert "ditutup" in r.json()["detail"]

    def test_ubah_status_lamaran_bikin_notifikasi(
        self, client, mahasiswa_token, mitra_token, magang_kegiatan, auth_header,
    ):
        # mahasiswa daftar
        r = client.post("/lamaran/", json={
            "mbkm_id": magang_kegiatan["mbkm_id"],
            "berkas_pendaftaran": berkas_lamaran(),
        }, headers=auth_header(mahasiswa_token))
        lamaran_id = r.json()["lamaran_id"]

        # mitra ubah status
        r = client.patch(
            f"/lamaran/{lamaran_id}/status",
            json={"status_pendaftaran": "diterima"},
            headers=auth_header(mitra_token),
        )
        assert r.status_code == 200

        # mahasiswa harusnya dapat notifikasi
        r = client.get("/notifikasi/saya", headers=auth_header(mahasiswa_token))
        assert r.status_code == 200
        notifs = r.json()
        assert len(notifs) == 1
        assert notifs[0]["jenis_notifikasi"] == "status_lamaran"

    def test_ubah_status_final_ditolak_domain_rule(
        self, client, mahasiswa_token, mitra_token, magang_kegiatan, auth_header,
    ):
        """Rule domain: lamaran yg sudah DITERIMA tidak bisa diubah."""
        r = client.post("/lamaran/", json={
            "mbkm_id": magang_kegiatan["mbkm_id"],
            "berkas_pendaftaran": berkas_lamaran(),
        }, headers=auth_header(mahasiswa_token))
        lamaran_id = r.json()["lamaran_id"]

        # ubah ke DITERIMA (sukses)
        client.patch(
            f"/lamaran/{lamaran_id}/status",
            json={"status_pendaftaran": "diterima"},
            headers=auth_header(mitra_token),
        )

        # coba ubah lagi (harus ditolak domain rule)
        r = client.patch(
            f"/lamaran/{lamaran_id}/status",
            json={"status_pendaftaran": "ditolak"},
            headers=auth_header(mitra_token),
        )
        assert r.status_code == 400
        assert "final" in r.json()["detail"].lower()

    def test_mahasiswa_lihat_lamaran_sendiri(
        self, client, mahasiswa_token, magang_kegiatan, auth_header,
    ):
        client.post("/lamaran/", json={
            "mbkm_id": magang_kegiatan["mbkm_id"],
            "berkas_pendaftaran": berkas_lamaran(),
        }, headers=auth_header(mahasiswa_token))
        r = client.get("/lamaran/saya", headers=auth_header(mahasiswa_token))
        assert r.status_code == 200
        assert len(r.json()) == 1

    def test_mitra_lihat_lamaran_untuk_kegiatannya(
        self, client, mahasiswa_token, mitra_token, magang_kegiatan, auth_header,
    ):
        client.post("/lamaran/", json={
            "mbkm_id": magang_kegiatan["mbkm_id"],
            "berkas_pendaftaran": berkas_lamaran(),
        }, headers=auth_header(mahasiswa_token))
        r = client.get(
            f"/lamaran/kegiatan/{magang_kegiatan['mbkm_id']}",
            headers=auth_header(mitra_token),
        )
        assert r.status_code == 200
        assert len(r.json()) == 1


# =========================================================
# Logbook
# =========================================================
class TestLogbook:
    def _lamaran_yang_diterima(self, client, mahasiswa_token, mitra_token, magang_kegiatan, auth_header) -> int:
        """Helper: bikin lamaran lalu terima-kan. Return lamaran_id."""
        r = client.post("/lamaran/", json={
            "mbkm_id": magang_kegiatan["mbkm_id"],
            "berkas_pendaftaran": berkas_lamaran(),
        }, headers=auth_header(mahasiswa_token))
        lamaran_id = r.json()["lamaran_id"]
        client.patch(
            f"/lamaran/{lamaran_id}/status",
            json={"status_pendaftaran": "diterima"},
            headers=auth_header(mitra_token),
        )
        return lamaran_id

    def test_tambah_logbook_sukses(
        self, client, mahasiswa_token, mitra_token, magang_kegiatan, auth_header,
    ):
        lamaran_id = self._lamaran_yang_diterima(
            client, mahasiswa_token, mitra_token, magang_kegiatan, auth_header,
        )
        r = client.post("/logbook/", json={
            "lamaran_id": lamaran_id,
            "aktivitas": "Onboarding di perusahaan",
            "durasi": 480, "tanggal": "2099-07-02",
        }, headers=auth_header(mahasiswa_token))
        assert r.status_code == 201
        assert r.json()["durasi"] == 480

    def test_upload_foto_logbook_sukses(
        self, client, mahasiswa_token, mitra_token, magang_kegiatan, auth_header, tmp_path, monkeypatch,
    ):
        monkeypatch.setattr("app.uploads.settings.upload_dir", str(tmp_path))
        lamaran_id = self._lamaran_yang_diterima(
            client, mahasiswa_token, mitra_token, magang_kegiatan, auth_header,
        )
        r = client.post(
            f"/logbook/lamaran/{lamaran_id}/upload-foto",
            files={"file": ("foto.jpg", b"isi foto", "image/jpeg")},
            headers=auth_header(mahasiswa_token),
        )
        assert r.status_code == 200
        body = r.json()
        assert body["foto"].startswith("/uploads/logbook/")

        r = client.post("/logbook/", json={
            "lamaran_id": lamaran_id,
            "aktivitas": "Dokumentasi kegiatan",
            "durasi": 120,
            "tanggal": "2099-07-03",
            "foto": body["foto"],
        }, headers=auth_header(mahasiswa_token))
        assert r.status_code == 201
        assert r.json()["foto"] == body["foto"]

    def test_logbook_untuk_lamaran_belum_diterima_ditolak(
        self, client, mahasiswa_token, magang_kegiatan, auth_header,
    ):
        r = client.post("/lamaran/", json={
            "mbkm_id": magang_kegiatan["mbkm_id"],
            "berkas_pendaftaran": berkas_lamaran(),
        }, headers=auth_header(mahasiswa_token))
        lamaran_id = r.json()["lamaran_id"]
        # status masih TELAH_MENDAFTAR
        r = client.post("/logbook/", json={
            "lamaran_id": lamaran_id,
            "aktivitas": "Kerja tanpa diterima?",
            "durasi": 60, "tanggal": "2099-07-02",
        }, headers=auth_header(mahasiswa_token))
        assert r.status_code == 400
        assert "DITERIMA" in r.json()["detail"]

    def test_list_logbook_per_lamaran(
        self, client, mahasiswa_token, mitra_token, magang_kegiatan, auth_header,
    ):
        lamaran_id = self._lamaran_yang_diterima(
            client, mahasiswa_token, mitra_token, magang_kegiatan, auth_header,
        )
        # tambah 2 logbook
        for i in range(2):
            client.post("/logbook/", json={
                "lamaran_id": lamaran_id, "aktivitas": f"Hari {i+1}",
                "durasi": 60, "tanggal": f"2099-07-0{i+2}",
            }, headers=auth_header(mahasiswa_token))

        r = client.get(
            f"/logbook/lamaran/{lamaran_id}",
            headers=auth_header(mahasiswa_token),
        )
        assert r.status_code == 200
        assert len(r.json()) == 2


# =========================================================
# Notifikasi
# =========================================================
class TestNotifikasi:
    def _siapkan_notifikasi(self, client, mahasiswa_token, mitra_token, magang_kegiatan, auth_header):
        r = client.post("/lamaran/", json={
            "mbkm_id": magang_kegiatan["mbkm_id"],
            "berkas_pendaftaran": berkas_lamaran(),
        }, headers=auth_header(mahasiswa_token))
        lamaran_id = r.json()["lamaran_id"]
        client.patch(
            f"/lamaran/{lamaran_id}/status",
            json={"status_pendaftaran": "wawancara"},
            headers=auth_header(mitra_token),
        )
        return lamaran_id

    def test_count_belum_dibaca(
        self, client, mahasiswa_token, mitra_token, magang_kegiatan, auth_header,
    ):
        self._siapkan_notifikasi(client, mahasiswa_token, mitra_token, magang_kegiatan, auth_header)
        r = client.get(
            "/notifikasi/saya/count-belum-dibaca",
            headers=auth_header(mahasiswa_token),
        )
        assert r.status_code == 200
        assert r.json()["jumlah"] == 1

    def test_tandai_dibaca(
        self, client, mahasiswa_token, mitra_token, magang_kegiatan, auth_header,
    ):
        self._siapkan_notifikasi(client, mahasiswa_token, mitra_token, magang_kegiatan, auth_header)
        r = client.get("/notifikasi/saya", headers=auth_header(mahasiswa_token))
        notif_id = r.json()[0]["notifikasi_id"]

        r = client.patch(
            f"/notifikasi/{notif_id}/baca",
            headers=auth_header(mahasiswa_token),
        )
        assert r.status_code == 200
        assert r.json()["status_baca"] is True

    def test_baca_semua(
        self, client, mahasiswa_token, mitra_token, magang_kegiatan, auth_header,
    ):
        self._siapkan_notifikasi(client, mahasiswa_token, mitra_token, magang_kegiatan, auth_header)
        r = client.post(
            "/notifikasi/saya/baca-semua",
            headers=auth_header(mahasiswa_token),
        )
        assert r.status_code == 204
        r = client.get(
            "/notifikasi/saya/count-belum-dibaca",
            headers=auth_header(mahasiswa_token),
        )
        assert r.json()["jumlah"] == 0


# =========================================================
# Update profil
# =========================================================
class TestProfilUpdate:
    def test_list_dan_detail_mitra_wajib_login(self, client, mitra_token, auth_header):
        r = client.get("/mitra/")
        assert r.status_code == 401

        r = client.get("/mitra/", headers=auth_header(mitra_token))
        assert r.status_code == 200
        body = r.json()
        assert len(body) == 1
        mitra_id = body[0]["mitra_id"]

        r = client.get(f"/mitra/{mitra_id}")
        assert r.status_code == 401

        r = client.get(f"/mitra/{mitra_id}", headers=auth_header(mitra_token))
        assert r.status_code == 200
        assert r.json()["nama_instansi"] == "PT Testing Corp"

    def test_update_profil_mahasiswa(self, client, mahasiswa_token, auth_header):
        r = client.patch("/mahasiswa/me", json={
            "nama": "Budi Updated", "angkatan": 2024,
        }, headers=auth_header(mahasiswa_token))
        assert r.status_code == 200
        body = r.json()
        assert body["nama"] == "Budi Updated"
        assert body["angkatan"] == 2024

    def test_update_profil_mitra(self, client, mitra_token, auth_header):
        r = client.patch("/mitra/me", json={
            "alamat": "Jl. Baru No. 99",
        }, headers=auth_header(mitra_token))
        assert r.status_code == 200
        assert r.json()["alamat"] == "Jl. Baru No. 99"
