from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from urllib.parse import quote

from app.config import settings
from app.database import get_db
from app.deps import get_current_user
from app.domain.mahasiswa import Mahasiswa
from app.domain.mitra import Mitra
from app.domain.user import User, UserRole
from app.email import send_notification_email
from app.repositories import MahasiswaRepository, MitraRepository, UserRepository
from app.schemas import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    MahasiswaRegister,
    MahasiswaResponse,
    MitraRegister,
    MitraResponse,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
)
from app.security import (
    create_access_token,
    create_password_reset_token,
    decode_password_reset_token,
    hash_password,
    verify_password,
)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register/mahasiswa",
    response_model=MahasiswaResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_mahasiswa(data: MahasiswaRegister, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    mahasiswa_repo = MahasiswaRepository(db)

    if user_repo.email_terdaftar(data.email):
        raise HTTPException(status_code=409, detail="Email sudah terdaftar")
    if mahasiswa_repo.nim_terdaftar(data.nim):
        raise HTTPException(status_code=409, detail="NIM sudah terdaftar")

    # buat domain objects
    new_user = User(
        nama=data.nama,
        email=data.email,
        password_hash=hash_password(data.password),
        role=UserRole.MAHASISWA,
    )
    new_user = user_repo.buat(new_user)  # dapet user_id

    new_mahasiswa = Mahasiswa(
        user_id=new_user.user_id,
        nama=new_user.nama,
        email=new_user.email,
        password_hash=new_user.password_hash,
        created_at=new_user.created_at,
        nim=data.nim,
        fakultas=data.fakultas,
        program_studi=data.program_studi,
        semester=data.semester,
    )
    new_mahasiswa = mahasiswa_repo.buat(new_mahasiswa)

    user_repo.commit()
    return new_mahasiswa


@router.post(
    "/register/mitra",
    response_model=MitraResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_mitra(data: MitraRegister, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    mitra_repo = MitraRepository(db)

    if user_repo.email_terdaftar(data.email):
        raise HTTPException(status_code=409, detail="Email sudah terdaftar")

    new_user = User(
        nama=data.nama,
        email=data.email,
        password_hash=hash_password(data.password),
        role=UserRole.MITRA,
    )
    new_user = user_repo.buat(new_user)

    new_mitra = Mitra(
        user_id=new_user.user_id,
        nama=new_user.nama,
        email=new_user.email,
        password_hash=new_user.password_hash,
        created_at=new_user.created_at,
        nama_instansi=data.nama_instansi,
        jenis_instansi=data.jenis_instansi,
        alamat=data.alamat,
        kontak=data.kontak,
    )
    new_mitra = mitra_repo.buat(new_mitra)

    user_repo.commit()
    return new_mitra


def _login_flow(email: str, password: str, db: Session) -> TokenResponse:
    user = UserRepository(db).get_by_email(email)
    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau password salah",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(user_id=user.user_id, role=user.role)
    return TokenResponse(access_token=token, role=user.role, user_id=user.user_id)


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Login via form (kompatibel dengan Swagger 'Authorize')."""
    return _login_flow(form_data.username, form_data.password, db)


@router.post("/login-json", response_model=TokenResponse)
def login_json(data: LoginRequest, db: Session = Depends(get_db)):
    """Login alternatif via JSON body."""
    return _login_flow(data.email, data.password, db)


@router.post("/forgot-password")
def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
) -> dict:
    """Kirim link reset password ke email user jika email terdaftar."""
    user = UserRepository(db).get_by_email(data.email)
    if user is not None:
        token = create_password_reset_token(user_id=user.user_id, role=user.role)
        reset_link = f"{settings.password_reset_url_base}?token={quote(token)}"
        message = (
            f"Halo {user.nama},\n\n"
            "Kami menerima permintaan untuk reset password akun Anda.\n"
            "Klik link berikut untuk membuat password baru:\n\n"
            f"{reset_link}\n\n"
            f"Link ini berlaku selama {settings.password_reset_token_expire_minutes} menit.\n"
            "Jika Anda tidak meminta reset password, abaikan email ini."
        )
        send_notification_email(
            to_email=user.email,
            subject="Reset Password IPB Internship & Career Tracker",
            message=message,
        )

    return {
        "message": (
            "Jika email terdaftar, instruksi reset password akan dikirim ke email tersebut."
        )
    }


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    try:
        payload = decode_password_reset_token(data.token)
        user_id = int(payload["sub"])
    except (ValueError, KeyError):
        raise HTTPException(status_code=400, detail="Token reset password tidak valid")

    repo = UserRepository(db)
    user = repo.get(user_id)
    if user is None:
        raise HTTPException(status_code=400, detail="Token reset password tidak valid")

    user.ganti_password(hash_password(data.password_baru))
    repo.simpan_perubahan(user)
    repo.commit()


@router.get("/me", response_model=UserResponse)
def profil_user(current: User = Depends(get_current_user)):
    return UserResponse(
        user_id=current.user_id,
        nama=current.nama,
        email=current.email,
        role=current.role,
        created_at=current.created_at,
    )


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    data: ChangePasswordRequest,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(data.password_lama, current.password_hash):
        raise HTTPException(status_code=400, detail="Password lama salah")

    current.ganti_password(hash_password(data.password_baru))  # method domain
    repo = UserRepository(db)
    repo.simpan_perubahan(current)
    repo.commit()
