from dataclasses import dataclass


@dataclass
class Mahasiswa:
    """Domain entity untuk profil mahasiswa."""
    user_id: int
    nama: str
    nim: str
    fakultas: str
    program_studi: str
    angkatan: int
    semester: int = 1
    mahasiswa_id: int | None = None

    def perbarui_profil(
        self,
        nama: str | None = None,
        fakultas: str | None = None,
        program_studi: str | None = None,
        angkatan: int | None = None,
        semester: int | None = None,
    ) -> None:
        if nama is not None:
            self.nama = nama
        if fakultas is not None:
            self.fakultas = fakultas
        if program_studi is not None:
            self.program_studi = program_studi
        if angkatan is not None:
            self.angkatan = angkatan
        if semester is not None:
            self.semester = semester

    def update_profil(
        self,
        nama: str | None = None,
        fakultas: str | None = None,
        program_studi: str | None = None,
        angkatan: int | None = None,
        semester: int | None = None,
    ) -> None:
        self.perbarui_profil(
            nama=nama,
            fakultas=fakultas,
            program_studi=program_studi,
            angkatan=angkatan,
            semester=semester,
        )
