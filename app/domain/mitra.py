from dataclasses import dataclass


@dataclass
class Mitra:
    """Domain entity untuk profil mitra/perusahaan."""
    user_id: int
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
        nama_instansi: str | None = None,
        jenis_instansi: str | None = None,
        alamat: str | None = None,
        kontak: str | None = None,
    ) -> None:
        self.perbarui_profil(
            nama_instansi=nama_instansi,
            jenis_instansi=jenis_instansi,
            alamat=alamat,
            kontak=kontak,
        )
