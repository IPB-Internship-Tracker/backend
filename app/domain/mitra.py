from dataclasses import dataclass, field

from app.domain.user import User, UserRole


@dataclass(kw_only=True)
class Mitra(User):
    """Domain entity mitra sebagai turunan dari User."""
    nama: str = ""
    email: str = ""
    password_hash: str = ""
    role: UserRole = field(default=UserRole.MITRA, init=False)
    nama_instansi: str
    jenis_instansi: str
    alamat: str
    kontak: str
    mitra_id: int | None = None

    def perbarui_profil(
        self,
        nama_instansi: str | None = None,
        jenis_instansi: str | None = None,
        alamat: str | None = None,
        kontak: str | None = None,
    ) -> None:
        if nama_instansi is not None:
            self.nama_instansi = nama_instansi
        if jenis_instansi is not None:
            self.jenis_instansi = jenis_instansi
        if alamat is not None:
            self.alamat = alamat
        if kontak is not None:
            self.kontak = kontak

    def update_profil(
        self,
        nama: str | None = None,
        email: str | None = None,
        nama_instansi: str | None = None,
        jenis_instansi: str | None = None,
        alamat: str | None = None,
        kontak: str | None = None,
    ) -> None:
        User.update_profil(self, nama=nama, email=email)
        self.perbarui_profil(
            nama_instansi=nama_instansi,
            jenis_instansi=jenis_instansi,
            alamat=alamat,
            kontak=kontak,
        )
