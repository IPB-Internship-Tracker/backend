"""
Script untuk membuat tabel-tabel di PostgreSQL.
Jalankan sekali setelah database PostgreSQL siap:

    python init_db.py

Untuk development kalau schema berubah dan data lama boleh dihapus:

    python init_db.py --drop
"""
import argparse

from app.database import Base, engine
from app import models  # noqa: F401


def main() -> None:
    parser = argparse.ArgumentParser(description="Inisialisasi tabel database.")
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Hapus semua tabel dulu lalu buat ulang. Pakai hanya untuk development.",
    )
    args = parser.parse_args()

    if args.drop:
        print("Menghapus tabel lama...")
        Base.metadata.drop_all(bind=engine)

    print("Membuat tabel-tabel...")
    Base.metadata.create_all(bind=engine)
    print("Selesai. Tabel tersedia:")
    for table in Base.metadata.tables:
        print(f"  - {table}")


if __name__ == "__main__":
    main()
