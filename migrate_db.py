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
    ALTER TABLE mahasiswa
    ADD COLUMN IF NOT EXISTS semester INTEGER
    """,
    """
    UPDATE mahasiswa
    SET semester = 1
    WHERE semester IS NULL
    """,
    """
    ALTER TABLE mahasiswa
    ALTER COLUMN semester SET NOT NULL
    """,
    """
    ALTER TABLE mahasiswa
    DROP COLUMN IF EXISTS angkatan
    """,
    """
    ALTER TABLE mahasiswa
    ADD COLUMN IF NOT EXISTS foto_profile VARCHAR(255)
    """,
    """
    CREATE TABLE IF NOT EXISTS kegiatan_draft (
        draft_id SERIAL PRIMARY KEY,
        mitra_id INTEGER NOT NULL REFERENCES mitra(mitra_id) ON DELETE CASCADE,
        kategori_mbkm kategorimbkm NOT NULL,
        data JSON NOT NULL DEFAULT '{}'::json,
        created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
        updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now()
    )
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
    """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_type WHERE typname = 'statusregistrasikegiatan'
        ) THEN
            CREATE TYPE statusregistrasikegiatan AS ENUM (
                'Registrasi Dibuka',
                'Registrasi Ditutup'
            );
        END IF;
    END $$;
    """,
    """
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'kegiatan_mbkm'
              AND column_name = 'status_kegiatan'
        ) AND NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'kegiatan_mbkm'
              AND column_name = 'status'
        ) THEN
            ALTER TABLE kegiatan_mbkm
            ADD COLUMN status statusregistrasikegiatan;

            UPDATE kegiatan_mbkm
            SET status = CASE
                WHEN deadline_pendaftaran < CURRENT_DATE
                  OR status_kegiatan::text IN (
                    'DITUTUP',
                    'ditutup',
                    'BERLANGSUNG',
                    'berlangsung',
                    'SELESAI',
                    'selesai',
                    'REGISTRASI_DITUTUP',
                    'Registrasi Ditutup'
                  )
                THEN 'Registrasi Ditutup'::statusregistrasikegiatan
                ELSE 'Registrasi Dibuka'::statusregistrasikegiatan
            END;

            ALTER TABLE kegiatan_mbkm
            ALTER COLUMN status SET NOT NULL;

            ALTER TABLE kegiatan_mbkm
            ALTER COLUMN status SET DEFAULT 'Registrasi Dibuka'::statusregistrasikegiatan;

            ALTER TABLE kegiatan_mbkm
            DROP COLUMN status_kegiatan;
        END IF;
    END $$;
    """,
    """
    UPDATE kegiatan_mbkm
    SET status = 'Registrasi Ditutup'::statusregistrasikegiatan
    WHERE deadline_pendaftaran < CURRENT_DATE
      AND status <> 'Registrasi Ditutup'::statusregistrasikegiatan
    """,
    """
    ALTER TABLE kegiatan_mbkm
    ALTER COLUMN status SET DEFAULT 'Registrasi Dibuka'::statusregistrasikegiatan
    """,
    """
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM pg_type WHERE typname = 'statuskegiatan'
        ) AND NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE udt_name = 'statuskegiatan'
        ) THEN
            DROP TYPE statuskegiatan;
        END IF;
    END $$;
    """,
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
    ALTER TABLE lomba
    ADD COLUMN IF NOT EXISTS poster VARCHAR(255)
    """,
    """
    UPDATE lomba
    SET poster = ''
    WHERE poster IS NULL
    """,
    """
    ALTER TABLE lomba
    ALTER COLUMN poster SET NOT NULL
    """,
    """
    ALTER TABLE lomba
    DROP COLUMN IF EXISTS tingkat_lomba
    """,
    """
    ALTER TABLE lomba
    DROP COLUMN IF EXISTS jenis_peserta
    """,
    """
    ALTER TABLE lomba
    DROP COLUMN IF EXISTS jumlah_anggota
    """,
    """
    ALTER TABLE lomba
    DROP COLUMN IF EXISTS hadiah
    """,
    """
    ALTER TABLE lomba
    DROP COLUMN IF EXISTS link_pendaftaran
    """,
    """
    ALTER TABLE studi_independen
    ADD COLUMN IF NOT EXISTS bidang VARCHAR(100)
    """,
    """
    UPDATE studi_independen
    SET bidang = 'Umum'
    WHERE bidang IS NULL
    """,
    """
    ALTER TABLE studi_independen
    ALTER COLUMN bidang SET NOT NULL
    """,
    """
    ALTER TABLE studi_independen
    ADD COLUMN IF NOT EXISTS poster VARCHAR(255)
    """,
    """
    UPDATE studi_independen
    SET poster = ''
    WHERE poster IS NULL
    """,
    """
    ALTER TABLE studi_independen
    ALTER COLUMN poster SET NOT NULL
    """,
    """
    ALTER TABLE studi_independen
    DROP COLUMN IF EXISTS kurikulum
    """,
    """
    ALTER TABLE studi_independen
    DROP COLUMN IF EXISTS metode_pembelajaran
    """,
    """
    ALTER TABLE studi_independen
    DROP COLUMN IF EXISTS benefit
    """,
    """
    ALTER TABLE studi_independen
    DROP COLUMN IF EXISTS link_pendaftaran
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
    # Berkas lamaran sekarang disimpan sebagai JSON mapping:
    # {"Curriculum Vitae (CV)": "path/cv.pdf", "Transkrip Nilai": "..."}
    """
    ALTER TABLE lamaran
    ADD COLUMN IF NOT EXISTS berkas_pendaftaran_json JSON
    """,
    """
    UPDATE lamaran
    SET berkas_pendaftaran_json = CASE
        WHEN berkas_pendaftaran_json IS NOT NULL THEN berkas_pendaftaran_json
        WHEN berkas_pendaftaran IS NULL THEN '{}'::json
        WHEN berkas_pendaftaran::text LIKE '{%' THEN berkas_pendaftaran::json
        ELSE json_build_object('Curriculum Vitae (CV)', berkas_pendaftaran)
    END
    """,
    """
    ALTER TABLE lamaran
    ALTER COLUMN berkas_pendaftaran_json SET NOT NULL
    """,
    """
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'lamaran' AND column_name = 'berkas_pendaftaran'
              AND data_type <> 'json'
        ) THEN
            ALTER TABLE lamaran DROP COLUMN berkas_pendaftaran;
            ALTER TABLE lamaran RENAME COLUMN berkas_pendaftaran_json TO berkas_pendaftaran;
        END IF;
    END $$;
    """,
    """
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'lamaran' AND column_name = 'berkas_pendaftaran'
              AND data_type = 'json'
        ) AND EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'lamaran' AND column_name = 'berkas_pendaftaran_json'
        ) THEN
            ALTER TABLE lamaran DROP COLUMN berkas_pendaftaran_json;
        END IF;
    END $$;
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
