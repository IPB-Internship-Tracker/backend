"""
Demo manual untuk security (password hashing + JWT).

Cara pakai:
    python coba_security.py
    python -i coba_security.py   # untuk masuk interactive mode
"""
from datetime import timedelta
import time

from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from app.models.user import UserRole


def section(judul: str) -> None:
    print("\n" + "=" * 60)
    print(f"  {judul}")
    print("=" * 60)


# =========================================================
# 1. PASSWORD HASHING
# =========================================================
section("Password hashing dengan bcrypt")

password_asli = "rahasia123"
hash1 = hash_password(password_asli)
hash2 = hash_password(password_asli)

print(f"Password asli : {password_asli}")
print(f"Hash ke-1     : {hash1}")
print(f"Hash ke-2     : {hash2}")
print(f"Hash sama?    : {hash1 == hash2}  <-- sengaja BEDA (bcrypt pakai salt)")
print()
print(f"verify('rahasia123', hash1) -> {verify_password('rahasia123', hash1)}")
print(f"verify('salah',      hash1) -> {verify_password('salah', hash1)}")
print(f"verify('rahasia123', hash2) -> {verify_password('rahasia123', hash2)}")
print()
print("Kesimpulan: meski hash-nya beda, password yang sama tetap cocok.")
print("Pihak ketiga TIDAK bisa membaca password asli dari hash.")


# =========================================================
# 2. JWT — token dengan masa berlaku normal
# =========================================================
section("JWT access token")

token = create_access_token(user_id=42, role=UserRole.MAHASISWA)
print(f"Token dibuat (untuk user_id=42, role=mahasiswa):")
print(f"  {token}")
print()
print("Struktur token: header.payload.signature (dipisah titik)")

payload = decode_access_token(token)
print(f"\nDecode isinya: {payload}")


# =========================================================
# 3. Token yang dimanipulasi -> ditolak
# =========================================================
section("Token diutak-atik / invalid -> ditolak")

for bad in ["bukan.token.valid", "abc", token + "x", ""]:
    try:
        decode_access_function = decode_access_token(bad)
        print(f"  BUG: '{bad[:20]}...' seharusnya ditolak")
    except ValueError as e:
        tampil = (bad[:30] + "...") if len(bad) > 30 else bad
        print(f"  Token '{tampil}' -> DITOLAK ({e})")


# =========================================================
# 4. Token yang sudah expired
# =========================================================
section("Token expired -> ditolak")

# bikin token yang sudah expired (masa berlaku -1 detik)
token_expired = create_access_token(
    user_id=99, role=UserRole.MITRA,
    expires_delta=timedelta(seconds=-1),
)
print(f"Token expired: {token_expired[:50]}...")
try:
    decode_access_token(token_expired)
    print("  BUG: harusnya ditolak")
except ValueError as e:
    print(f"  DITOLAK: {e}")


print("\n" + "=" * 60)
print("  Selesai. Edit file ini untuk eksperimen lain.")
print("=" * 60)