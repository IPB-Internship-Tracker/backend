"""
Migrasi ringan untuk database development yang sudah pernah dibuat.

Script ini menaikkan schema lama ke field terbaru tanpa menghapus tabel/data.
Jalankan setelah PostgreSQL aktif:

    python migrate_db.py
"""
from sqlalchemy import text

from app.database import engine


PRE_COMMIT_MIGRATIONS = [

    """
    ALTER TYPE statuslamaran ADD VALUE IF NOT EXISTS 'TELAH_MENDAFTAR'
    """,
]


MIGRATIONS = [

    """
    ALTER TABLE kegiatan_mbkm
    ADD COLUMN IF NOT EXISTS narahubung VARCHAR(150)
    """,
    """
    UPDATE kegiatan_mbkm
    SET narahubung = 'Narahubung belum diisi'
    WHERE narahubung IS NULL
    """,
    """
    ALTER TABLE kegiatan_mbkm
    ALTER COLUMN narahubung SET NOT NULL
    """,
    """
    ALTER TABLE kegiatan_mbkm
    ADD COLUMN IF NOT EXISTS info_lebih_lanjut TEXT
    """,
    """
    UPDATE kegiatan_mbkm
    SET info_lebih_lanjut = 'Belum tersedia'
    WHERE info_lebih_lanjut IS NULL
    """,
    """
    ALTER TABLE kegiatan_mbkm
    ALTER COLUMN info_lebih_lanjut SET NOT NULL
    """,
    # Label enum lama dibiarkan agar migrasi aman, tetapi row lama dinormalisasi
    # ke status yang dipakai aplikasi sekarang.
    """
    UPDATE lamaran
    SET status_pendaftaran = 'TELAH_MENDAFTAR'
    WHERE status_pendaftaran::text = 'VERIFIKASI_BERKAS'
    """,
    """
    UPDATE lamaran
    SET status_pendaftaran = 'DITOLAK'
    WHERE status_pendaftaran::text = 'BERKAS_DITOLAK'
    """,
    # Field magang baru. Kolom lama lokasi/uang_saku dibiarkan sebagai arsip
    # kompatibilitas, sementara aplikasi memakai kota_lokasi/gaji_perbulan.
    """
    ALTER TABLE magang
    ADD COLUMN IF NOT EXISTS nama_perusahaan VARCHAR(200)
    """,
    """
    UPDATE magang m
    SET nama_perusahaan = COALESCE(mi.nama_instansi, 'Perusahaan belum diisi')
    FROM kegiatan_mbkm k
    LEFT JOIN mitra mi ON mi.mitra_id = k.mitra_id
    WHERE k.mbkm_id = m.mbkm_id
      AND m.nama_perusahaan IS NULL
    """,
    """
    ALTER TABLE magang
    ALTER COLUMN nama_perusahaan SET NOT NULL
    """,
    """
    ALTER TABLE magang
    ADD COLUMN IF NOT EXISTS logo_url VARCHAR(255)
    """,
    """
    ALTER TABLE magang
    ADD COLUMN IF NOT EXISTS penempatan penempatanmagang
    """,
    """
    UPDATE magang
    SET penempatan = 'WFO'
    WHERE penempatan IS NULL
    """,
    """
    ALTER TABLE magang
    ALTER COLUMN penempatan SET NOT NULL
    """,
    """
    ALTER TABLE magang
    ADD COLUMN IF NOT EXISTS kota_lokasi VARCHAR(150)
    """,
    """
    UPDATE magang
    SET kota_lokasi = COALESCE(NULLIF(lokasi, ''), 'Lokasi belum diisi')
    WHERE kota_lokasi IS NULL
    """,
    """
    ALTER TABLE magang
    ALTER COLUMN kota_lokasi SET NOT NULL
    """,
    """
    ALTER TABLE magang
    ADD COLUMN IF NOT EXISTS alamat_lengkap VARCHAR(255)
    """,
    """
    UPDATE magang m
    SET alamat_lengkap = COALESCE(NULLIF(mi.alamat, ''), NULLIF(m.lokasi, ''), 'Alamat belum diisi')
    FROM kegiatan_mbkm k
    LEFT JOIN mitra mi ON mi.mitra_id = k.mitra_id
    WHERE k.mbkm_id = m.mbkm_id
      AND m.alamat_lengkap IS NULL
    """,
    """
    ALTER TABLE magang
    ALTER COLUMN alamat_lengkap SET NOT NULL
    """,
    """
    ALTER TABLE magang
    ADD COLUMN IF NOT EXISTS tipe_gaji tipegaji
    """,
    """
    UPDATE magang
    SET tipe_gaji = CASE
        WHEN COALESCE(uang_saku, 0) > 0 THEN 'PAID'::tipegaji
        ELSE 'UNPAID'::tipegaji
    END
    WHERE tipe_gaji IS NULL
    """,
    """
    ALTER TABLE magang
    ALTER COLUMN tipe_gaji SET NOT NULL
    """,
    """
    ALTER TABLE magang
    ADD COLUMN IF NOT EXISTS gaji_perbulan DOUBLE PRECISION
    """,
    """
    UPDATE magang
    SET gaji_perbulan = COALESCE(uang_saku, 0)
    WHERE gaji_perbulan IS NULL
    """,
    """
    ALTER TABLE magang
    ALTER COLUMN gaji_perbulan SET NOT NULL
    """,
    """
    ALTER TABLE magang
    ADD COLUMN IF NOT EXISTS dokumen_dibutuhkan JSON
    """,
    """
    UPDATE magang
    SET dokumen_dibutuhkan = '["Curriculum Vitae (CV)"]'::json
    WHERE dokumen_dibutuhkan IS NULL
    """,
    """
    ALTER TABLE magang
    ALTER COLUMN dokumen_dibutuhkan SET NOT NULL
    """,
    # Kolom lama tidak lagi dipakai ORM baru. Dibuat nullable agar INSERT baru
    # tidak gagal di database lama yang masih menyimpan kolom ini.
    """
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'magang' AND column_name = 'lokasi'
        ) THEN
            ALTER TABLE magang ALTER COLUMN lokasi DROP NOT NULL;
        END IF;
    END $$;
    """,
    """
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'magang' AND column_name = 'uang_saku'
        ) THEN
            ALTER TABLE magang ALTER COLUMN uang_saku DROP NOT NULL;
        END IF;
    END $$;
    """,
    # Ubah bidang lama (varchar, biasanya "IT") menjadi enum baru.
    """
    ALTER TABLE magang
    ALTER COLUMN bidang TYPE bidangmagang
    USING (
        CASE
            WHEN bidang IN (
                'INFORMATION_TECHNOLOGY',
                'DATA_ANALYTICS',
                'BUSINESS_MANAGEMENT',
                'MARKETING_COMMUNICATION',
                'FINANCE_ACCOUNTING',
                'HUMAN_RESOURCES',
                'OPERATIONS_LOGISTICS',
                'ADMINISTRATION',
                'DESIGN_CREATIVE',
                'ENGINEERING_NON_IT',
                'RESEARCH_DEVELOPMENT',
                'SALES_BUSINESS_DEVELOPMENT',
                'LEGAL',
                'HEALTHCARE_LIFE_SCIENCES'
            )
            THEN bidang::bidangmagang
            ELSE 'INFORMATION_TECHNOLOGY'::bidangmagang
        END
    )
    """,
]


def main() -> None:
    print("Menjalankan migrasi database...")
    with engine.begin() as conn:
        for sql in PRE_COMMIT_MIGRATIONS:
            conn.execute(text(sql))

    with engine.begin() as conn:
        for sql in MIGRATIONS:
            conn.execute(text(sql))
    print("Selesai. Schema database sudah sesuai versi terbaru.")


if __name__ == "__main__":
    main()
