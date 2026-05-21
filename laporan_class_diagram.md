# Laporan Kesesuaian Class Diagram dengan Implementasi Kode

## 1. Gambaran Umum Struktur Kode

Repository ini menggunakan pola backend FastAPI dengan pemisahan layer sebagai berikut:

| Layer | Fungsi | Lokasi kode |
|---|---|---|
| Domain/entity | Merepresentasikan objek bisnis dan aturan bisnis, misalnya `User`, `Mahasiswa`, `KegiatanMBKM`, `Lamaran`, dan `Logbook`. | `app/domain/` |
| ORM/model database | Merepresentasikan tabel database SQLAlchemy, misalnya `UserORM`, `MahasiswaORM`, `KegiatanMBKMORM`, `LamaranORM`. | `app/models/` |
| Schema/DTO | Validasi request dan bentuk response API menggunakan Pydantic. | `app/schemas/` |
| Repository | Mengakses database dan mengubah data ORM menjadi domain entity. | `app/repositories/` |
| Controller/API route | Endpoint FastAPI yang menerima request, memanggil domain/repository, dan mengembalikan response. | `app/routes/` |
| App registration | Mendaftarkan router dan membuat tabel saat startup. | `app/main.py` |

Catatan: kode ini tidak memiliki folder `services` eksplisit. Peran service sebagian besar dibagi antara `app/routes/` sebagai controller, `app/domain/` untuk business rule, dan `app/repositories/` untuk akses data.

## 2. Pemetaan Class Diagram ke Implementasi Kode

| Elemen class diagram | Implementasi model/entity | Service/controller/repository | Struktur kode yang digunakan | Status |
|---|---|---|---|---|
| `user` | `User` domain entity dan `UserORM` tabel `users` | `auth.py`, `UserRepository`, `security.py` | `app/domain/user.py`, `app/models/user.py`, `app/routes/auth.py`, `app/repositories/user_repository.py` | Sesuai sebagian |
| `user_id`, `nama`, `email`, `password`, `role` | `User.user_id`, `nama`, `email`, `password_hash`, `role`; ORM menyimpan `password` sebagai hash | Register, login, change password | `UserORM` pada tabel `users` | Sesuai, tetapi password di kode disimpan sebagai hash |
| `login(email, password)` | Tidak menjadi method di entity `User` | Fungsi `_login_flow()`, endpoint `/auth/login` dan `/auth/login-json` | `app/routes/auth.py` | Berbeda lokasi implementasi |
| `logout()` | Tidak ditemukan implementasi khusus | Tidak ada endpoint logout | - | Belum diimplementasikan |
| `updateProfil(nama, email)` | Tidak ada method persis di `User`; ada `UserUpdate` schema tetapi belum ada route update user umum | Update profil mahasiswa/mitra dilakukan terpisah | `app/routes/mahasiswa.py`, `app/routes/mitra.py`, `app/domain/mahasiswa.py`, `app/domain/mitra.py` | Berbeda |
| `mahasiswa` | `Mahasiswa` domain entity dan `MahasiswaORM` tabel `mahasiswa` | `MahasiswaRepository`, route `/mahasiswa` | `app/domain/mahasiswa.py`, `app/models/mahasiswa.py`, `app/routes/mahasiswa.py` | Sesuai sebagian |
| `nim : int` | `nim` bertipe string dengan panjang 11 karakter | Validasi NIM IPB di schema | `app/schemas/mahasiswa.py` | Berbeda tipe data |
| `semester : int` | Tidak ada field `semester`; kode memakai `angkatan` | Register/update mahasiswa | `app/domain/mahasiswa.py`, `app/models/mahasiswa.py` | Berbeda nama dan makna field |
| `mitra` | `Mitra` domain entity dan `MitraORM` tabel `mitra` | `MitraRepository`, route `/mitra` | `app/domain/mitra.py`, `app/models/mitra.py`, `app/routes/mitra.py` | Sesuai sebagian |
| `nama_instansi`, `jenis_instansi` | Ada di domain dan ORM | Register/update mitra | `app/domain/mitra.py`, `app/models/mitra.py` | Sesuai |
| Tambahan field mitra | Kode menambahkan `alamat` dan `kontak` | Dipakai saat register/update mitra | `app/schemas/mitra.py`, `app/models/mitra.py` | Tambahan di kode |
| `kegiatan_mbkm` | `KegiatanMBKM` domain entity dan `KegiatanMBKMORM` tabel `kegiatan_mbkm` | `KegiatanRepository`, route `/kegiatan` | `app/domain/kegiatan.py`, `app/models/kegiatan.py`, `app/routes/kegiatan.py` | Sesuai sebagian |
| `kegiatan_id` | Kode memakai `mbkm_id` | Dipakai pada endpoint detail/update/delete | `app/models/kegiatan.py`, `app/routes/kegiatan.py` | Berbeda nama field |
| `kategori` | Kode memakai `kategori_mbkm` enum | Filter list kegiatan | `app/domain/kegiatan.py`, `app/schemas/kegiatan.py` | Berbeda nama field |
| `status_kegiatan` | `StatusKegiatan` enum: `dibuka`, `ditutup`, `berlangsung`, `selesai` | Tutup pendaftaran dan filter kegiatan | `app/domain/kegiatan.py`, `app/routes/kegiatan.py` | Sesuai, lebih spesifik karena enum |
| `tambah()`, `edit()`, `hapus()` | Tidak ada method entity dengan nama tersebut | CRUD ada pada route dan repository: `buat`, `simpan_perubahan`, `hapus` | `app/repositories/kegiatan_repository.py`, `app/routes/kegiatan.py` | Implementasi dipisah ke controller/repository |
| `getMbkmList()`, `getDetailById()` | Tidak ada method dengan nama persis | `KegiatanRepository.list()`, `KegiatanRepository.get()`, endpoint `GET /kegiatan`, `GET /kegiatan/{mbkm_id}` | `app/repositories/kegiatan_repository.py`, `app/routes/kegiatan.py` | Sesuai fungsi, beda nama |
| `magang` | `Magang` domain entity dan `MagangORM` tabel `magang` | Endpoint `/kegiatan/magang` | `app/domain/kegiatan.py`, `app/models/kegiatan.py`, `app/routes/kegiatan.py` | Sesuai sebagian |
| `lokasi`, `uang_saku` | Kode terbaru memakai `kota_lokasi` dan `gaji_perbulan`; domain masih menyediakan alias `lokasi` dan `uang_saku` | Create/update magang | `app/domain/kegiatan.py`, `app/schemas/kegiatan.py`, `app/models/kegiatan.py` | Berbeda, tetapi ada kompatibilitas alias |
| Tambahan field magang | `nama_perusahaan`, `logo_url`, `penempatan`, `alamat_lengkap`, `tipe_gaji`, `dokumen_dibutuhkan` | Create/update/list/detail magang | `app/schemas/kegiatan.py`, `app/models/kegiatan.py` | Tambahan di kode |
| `lomba` | `Lomba` domain entity dan `LombaORM` tabel `lomba` | Endpoint `/kegiatan/lomba` | `app/domain/kegiatan.py`, `app/models/kegiatan.py`, `app/routes/kegiatan.py` | Sesuai sebagian |
| `jenis_peserta : int` | Kode memakai `jenis_peserta : str` | Create/update lomba | `app/domain/kegiatan.py`, `app/models/kegiatan.py`, `app/schemas/kegiatan.py` | Berbeda tipe data |
| `studi_independen` | `StudiIndependen` domain entity dan `StudiIndependenORM` tabel `studi_independen` | Endpoint `/kegiatan/studi-independen` | `app/domain/kegiatan.py`, `app/models/kegiatan.py`, `app/routes/kegiatan.py` | Sesuai |
| `lamaran` | `Lamaran` domain entity dan `LamaranORM` tabel `lamaran` | `LamaranRepository`, route `/lamaran` | `app/domain/lamaran.py`, `app/models/lamaran.py`, `app/routes/lamaran.py` | Sesuai sebagian |
| `berkas_pendaftaran : List<File>` | Kode memakai `berkas_pendaftaran : str` sebagai path/URL berkas | Create/update lamaran | `app/schemas/lamaran.py`, `app/models/lamaran.py` | Berbeda tipe data |
| `status_pendaftaran : string` | Kode memakai enum `StatusLamaran`: `telah_mendaftar`, `wawancara`, `diterima`, `ditolak` | Ubah status lamaran | `app/domain/lamaran.py`, `app/routes/lamaran.py` | Sesuai fungsi, lebih spesifik |
| `ubahStatus(status)` | `Lamaran.ubah_status(status_baru)` | Endpoint `PATCH /lamaran/{lamaran_id}/status` | `app/domain/lamaran.py`, `app/routes/lamaran.py` | Sesuai, beda gaya penamaan |
| `getStatus()` | Tidak ada method dengan nama ini | Status dibaca langsung dari `status_pendaftaran` | `app/domain/lamaran.py` | Tidak diimplementasikan sebagai method |
| `tambahBerkas(file)`, `hapusBerkas(file)` | Tidak ada method khusus | Berkas hanya satu string path/URL | `app/schemas/lamaran.py`, `app/models/lamaran.py` | Belum sesuai diagram |
| `getLamaranByMahasiswa(MhsId)` | `LamaranRepository.list_by_mahasiswa()` | Endpoint `GET /lamaran/saya` | `app/repositories/lamaran_repository.py`, `app/routes/lamaran.py` | Sesuai fungsi, beda nama |
| `validate()` | Tidak ada method `validate()` di entity | Validasi dilakukan oleh schema, route, dan business rule domain | `app/schemas/lamaran.py`, `app/routes/lamaran.py`, `app/domain/lamaran.py` | Berbeda lokasi implementasi |
| `logbook` | `Logbook` domain entity dan `LogbookORM` tabel `logbook` | `LogbookRepository`, route `/logbook` | `app/domain/logbook.py`, `app/models/logbook.py`, `app/routes/logbook.py` | Sesuai sebagian |
| `kegiatan_perhari` | Kode memakai `aktivitas` | Create/update logbook | `app/domain/logbook.py`, `app/schemas/logbook.py`, `app/models/logbook.py` | Berbeda nama field |
| `foto : blob` | Kode memakai `foto : str | None`, biasanya path/URL file | Create/update logbook | `app/models/logbook.py`, `app/schemas/logbook.py` | Berbeda tipe data |
| Method logbook `tambahLogbook`, `edit`, `hapus`, `getLogbookByLamaran`, `getLogbookById` | Method langsung di entity tidak ada; operasi ada di repository dan route | `tambah_logbook`, `update_logbook`, `hapus_logbook`, `list_by_lamaran`, `get` | `app/routes/logbook.py`, `app/repositories/logbook_repository.py` | Sesuai fungsi, beda layer/nama |
| `notifikasi` | `Notifikasi` domain entity dan `NotifikasiORM` tabel `notifikasi` | `NotifikasiRepository`, route `/notifikasi` | `app/domain/notifikasi.py`, `app/models/notifikasi.py`, `app/routes/notifikasi.py` | Sesuai sebagian |
| Relasi notifikasi ke mahasiswa | Kode menghubungkan notifikasi ke `users.user_id`, bukan langsung ke `mahasiswa_id` | Notifikasi status lamaran dikirim ke `mhs.user_id` | `app/models/notifikasi.py`, `app/routes/lamaran.py` | Berbeda relasi langsung |
| `kirimEmail()`, `kirimWeb()` | Tidak ada method pengiriman email/web | Notifikasi dibuat sebagai data dan dibaca lewat API | `app/routes/notifikasi.py`, `app/repositories/notifikasi_repository.py` | Belum diimplementasikan |
| `getNotifikasiByMahasiswa(MhsId)` | Tidak ada query langsung berdasarkan `mahasiswa_id` | `NotifikasiRepository.list_by_user(user_id)` dan endpoint `/notifikasi/saya` | `app/repositories/notifikasi_repository.py`, `app/routes/notifikasi.py` | Sesuai kebutuhan user login, beda parameter |

## 3. Perbedaan Utama antara Class Diagram dan Kode

| Bagian | Di class diagram | Di kode repository | Keterangan |
|---|---|---|---|
| Hubungan `User`, `Mahasiswa`, `Mitra` | `Mahasiswa` dan `Mitra` digambarkan sebagai turunan/inheritance dari `User` | `Mahasiswa` dan `Mitra` memiliki relasi 1:1 ke `User` melalui `user_id` | Perbedaan desain paling besar. Kode memakai composition/foreign key, bukan inheritance. |
| Role user | Role string | Enum `UserRole` dengan `mahasiswa`, `mitra`, `admin` | Kode memiliki role tambahan `admin`. |
| Password | `password : string` | `password_hash` di domain, kolom ORM bernama `password` berisi hash | Lebih aman di kode karena tidak menyimpan plaintext. |
| Profil user | Ada `updateProfil(nama, email)` di `User` | Update profil dipisah ke mahasiswa/mitra; belum ada endpoint update email umum | Perlu disesuaikan jika laporan ingin mengikuti kode. |
| Mahasiswa | Memiliki `semester` | Memiliki `angkatan` | Jika diagram mengikuti kode, `semester` sebaiknya diganti menjadi `angkatan`. |
| NIM | `nim : int` | `nim : str` | NIM lebih tepat string karena diawali huruf dan panjang tetap 11 karakter. |
| Kegiatan MBKM | `kegiatan_id`, `kategori` | `mbkm_id`, `kategori_mbkm` | Perbedaan nama atribut. |
| Kegiatan MBKM | Tidak memuat `syarat_ketentuan` | Kode memiliki `syarat_ketentuan` | Field ini perlu ditambahkan ke diagram jika mengikuti kode. |
| Magang | `lokasi`, `uang_saku` | `kota_lokasi`, `gaji_perbulan`, serta beberapa field tambahan | Diagram masih memakai istilah lama; kode menyediakan alias domain untuk kompatibilitas. |
| Lomba | `jenis_peserta : int` | `jenis_peserta : str` | Di kode, jenis peserta berupa teks, misalnya individu/tim. |
| Lamaran | `berkas_pendaftaran : List<File>` | `berkas_pendaftaran : str` | Kode hanya menyimpan path/URL, bukan daftar file. |
| Logbook | `foto : blob`, `kegiatan_perhari` | `foto : str | None`, `aktivitas` | Kode menyimpan referensi foto, bukan blob langsung. |
| Notifikasi | Terhubung ke `Mahasiswa` | Terhubung ke `User` | Dengan desain kode, semua role user bisa menerima notifikasi. |
| Method di class diagram | Banyak method CRUD berada di entity | CRUD ada di `routes` dan `repositories`; entity hanya memuat business rule | Ini sesuai pola clean/domain separation yang dipakai repo. |
| Service layer | Tersirat seperti `OrderService` pada contoh laporan | Tidak ada folder/class service eksplisit | Untuk laporan, `routes` bisa disebut controller dan `repositories` bisa disebut layer akses data. |

## 4. Kesesuaian Relasi

| Relasi di class diagram | Implementasi di kode | Status |
|---|---|---|
| `User` ke `Mahasiswa` | `users.user_id` ke `mahasiswa.user_id`, unique 1:1 | Sesuai secara relasi, tetapi bukan inheritance |
| `User` ke `Mitra` | `users.user_id` ke `mitra.user_id`, unique 1:1 | Sesuai secara relasi, tetapi bukan inheritance |
| `Mitra` 1 ke 0..* `KegiatanMBKM` | `KegiatanMBKMORM.mitra_id` foreign key ke `mitra.mitra_id` | Sesuai |
| `KegiatanMBKM` diwarisi `Magang`, `Lomba`, `StudiIndependen` | Joined-table inheritance SQLAlchemy dan inheritance domain dataclass | Sesuai |
| `Mahasiswa` 1 ke 0..* `Lamaran` | `LamaranORM.mahasiswa_id` foreign key ke `mahasiswa.mahasiswa_id` | Sesuai |
| `KegiatanMBKM` 1 ke 0..* `Lamaran` | `LamaranORM.mbkm_id` foreign key ke `kegiatan_mbkm.mbkm_id` | Sesuai |
| `Lamaran` 1 ke 0..* `Logbook` | `LogbookORM.lamaran_id` foreign key ke `lamaran.lamaran_id` dengan cascade delete-orphan | Sesuai |
| `Mahasiswa` 1 ke 0..* `Notifikasi` | Kode memakai `NotifikasiORM.user_id` ke `users.user_id` | Berbeda relasi langsung |

## 5. Kesimpulan

Secara umum, class diagram sudah menggambarkan domain utama sistem, yaitu user, mahasiswa, mitra, kegiatan MBKM, lamaran, logbook, dan notifikasi. Implementasi kode juga memiliki semua entity utama tersebut.

Namun, terdapat beberapa perbedaan desain yang perlu dicatat dalam laporan:

1. Kode tidak memakai inheritance langsung dari `User` ke `Mahasiswa`/`Mitra`, tetapi memakai relasi 1:1 melalui `user_id`.
2. Method CRUD pada diagram tidak selalu berada di entity, karena kode memindahkan operasi tersebut ke layer route/controller dan repository.
3. Beberapa atribut pada diagram berbeda dengan kode, terutama `semester` vs `angkatan`, `kegiatan_id` vs `mbkm_id`, `lokasi`/`uang_saku` vs `kota_lokasi`/`gaji_perbulan`, serta `kegiatan_perhari` vs `aktivitas`.
4. Beberapa fitur pada diagram belum ada di kode, seperti `logout()`, `kirimEmail()`, `kirimWeb()`, dan pengelolaan banyak file lamaran dengan `List<File>`.
5. Kode memiliki beberapa field tambahan yang tidak ada di diagram, seperti `alamat` dan `kontak` pada mitra, `syarat_ketentuan` pada kegiatan, serta detail tambahan pada magang.

Jika class diagram ingin dibuat benar-benar mengikuti kode repository, diagram perlu diperbarui pada bagian relasi `User`-`Mahasiswa`-`Mitra`, atribut mahasiswa, atribut magang, atribut logbook, dan relasi notifikasi.
