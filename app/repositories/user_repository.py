"""
Repository: layer yang boleh akses ORM.
Tugasnya: konversi bolak-balik antara UserORM <-> User (domain).
"""
from sqlalchemy.orm import Session

from app.domain.user import User, UserRole
from app.models.user import UserORM


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ---------- mapping ORM <-> Domain ----------
    @staticmethod
    def _to_domain(orm: UserORM) -> User:
        return User(
            user_id=orm.user_id,
            nama=orm.nama,
            email=orm.email,
            password_hash=orm.password,
            role=orm.role,
            created_at=orm.created_at,
        )

    # ---------- query ----------
    def get(self, user_id: int) -> User | None:
        orm = self.db.get(UserORM, user_id)
        return self._to_domain(orm) if orm else None

    def get_by_email(self, email: str) -> User | None:
        orm = self.db.query(UserORM).filter(UserORM.email == email.lower()).first()
        return self._to_domain(orm) if orm else None

    def email_terdaftar(self, email: str) -> bool:
        return self.db.query(UserORM).filter(UserORM.email == email.lower()).first() is not None

    # ---------- mutation ----------
    def buat(self, user: User) -> User:
        orm = UserORM(
            nama=user.nama,
            email=user.email.lower(),
            password=user.password_hash,
            role=user.role,
        )
        self.db.add(orm)
        self.db.flush()  # supaya dapat user_id tanpa commit
        self.db.refresh(orm)
        user.user_id = orm.user_id
        user.created_at = orm.created_at
        return user

    def simpan_perubahan(self, user: User) -> User:
        """Update user yang sudah ada (berdasarkan user_id)."""
        orm = self.db.get(UserORM, user.user_id)
        if orm is None:
            raise ValueError(f"User dengan id={user.user_id} tidak ada")
        orm.nama = user.nama
        orm.email = user.email.lower()
        orm.password = user.password_hash
        orm.role = user.role
        return user

    def commit(self) -> None:
        self.db.commit()
