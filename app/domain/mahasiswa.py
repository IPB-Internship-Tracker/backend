from dataclasses import dataclass, field

from app.domain.user import User, UserRole


@dataclass(kw_only=True)
class Mahasiswa(User):
    """Domain entity mahasiswa sebagai turunan dari User."""
    email: str = ""
    password_hash: str = ""
    role: UserRole = field(default=UserRole.MAHASISWA, init=False)
    nim: str
    fakultas: str
    program_studi: str
    semester: int = 1
    foto_profile: str | None = None
    mahasiswa_id: int | None = None

    def perbarui_profil(
        self,
        nama: str | None = None,
        fakultas: str | None = None,
        program_studi: str | None = None,
        semester: int | None = None,
        foto_profile: str | None = None,
    ) -> None:
        if nama is not None:
            self.nama = nama
        if fakultas is not None:
            self.fakultas = fakultas
        if program_studi is not None:
            self.program_studi = program_studi
        if semester is not None:
            self.semester = semester
        if foto_profile is not None:
            self.foto_profile = foto_profile

    def update_profil(
        self,
        nama: str | None = None,
        email: str | None = None,
        fakultas: str | None = None,
        program_studi: str | None = None,
        semester: int | None = None,
        foto_profile: str | None = None,
    ) -> None:
        User.update_profil(self, nama=nama, email=email)
        self.perbarui_profil(
            fakultas=fakultas,
            program_studi=program_studi,
            semester=semester,
            foto_profile=foto_profile,
        )
