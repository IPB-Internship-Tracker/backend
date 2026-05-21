"""
Repository polymorphic untuk KegiatanMBKM + Magang + Lomba + StudiIndependen.
Ini convert dua arah antara ORM (dgn hirarki joined-table inheritance) dan Domain.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.domain.kegiatan import (
    DokumenLamaran,
    KategoriMBKM,
    KegiatanMBKM,
    Lomba,
    Magang,
    StatusKegiatan,
    StudiIndependen,
)
from app.models.kegiatan import (
    KegiatanMBKMORM,
    LombaORM,
    MagangORM,
    StudiIndependenORM,
)


class KegiatanRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ---------- ORM -> Domain ----------
    @staticmethod
    def _dokumen_to_domain(raw: list[str] | None) -> list[DokumenLamaran | str]:
        hasil: list[DokumenLamaran | str] = []
        for item in raw or []:
            try:
                hasil.append(DokumenLamaran(item))
            except ValueError:
                hasil.append(item)
        return hasil

    @staticmethod
    def _dokumen_to_storage(dokumen: list[DokumenLamaran | str]) -> list[str]:
        return [item.value if isinstance(item, DokumenLamaran) else item for item in dokumen]

    @staticmethod
    def _to_domain(orm: KegiatanMBKMORM) -> KegiatanMBKM:
        base = dict(
            mbkm_id=orm.mbkm_id,
            mitra_id=orm.mitra_id,
            nama_kegiatan=orm.nama_kegiatan,
            deskripsi=orm.deskripsi,
            kategori_mbkm=orm.kategori_mbkm,
            deadline_pendaftaran=orm.deadline_pendaftaran,
            kuota=orm.kuota,
            tanggal_mulai=orm.tanggal_mulai,
            tanggal_selesai=orm.tanggal_selesai,
            syarat_ketentuan=orm.syarat_ketentuan,
            narahubung=orm.narahubung,
            info_lebih_lanjut=orm.info_lebih_lanjut,
            status_kegiatan=orm.status_kegiatan,
        )
        if isinstance(orm, MagangORM):
            return Magang(
                **base,
                bidang=orm.bidang,
                posisi=orm.posisi,
                nama_perusahaan=orm.nama_perusahaan,
                logo_url=orm.logo_url,
                penempatan=orm.penempatan,
                kota_lokasi=orm.kota_lokasi,
                alamat_lengkap=orm.alamat_lengkap,
                tipe_gaji=orm.tipe_gaji,
                gaji_perbulan=orm.gaji_perbulan,
                dokumen_dibutuhkan=KegiatanRepository._dokumen_to_domain(
                    orm.dokumen_dibutuhkan
                ),
            )
        if isinstance(orm, LombaORM):
            return Lomba(
                **base,
                bidang=orm.bidang,
                tingkat_lomba=orm.tingkat_lomba,
                jenis_peserta=orm.jenis_peserta,
                jumlah_anggota=orm.jumlah_anggota,
                hadiah=orm.hadiah,
            )
        if isinstance(orm, StudiIndependenORM):
            return StudiIndependen(
                **base,
                kurikulum=orm.kurikulum,
                metode_pembelajaran=orm.metode_pembelajaran,
                benefit=orm.benefit,
            )
        return KegiatanMBKM(**base)

    # ---------- Query ----------
    def get(self, mbkm_id: int) -> KegiatanMBKM | None:
        orm = self.db.get(KegiatanMBKMORM, mbkm_id)
        return self._to_domain(orm) if orm else None

    def get_detail_by_id(self, mbkm_id: int) -> KegiatanMBKM | None:
        return self.get(mbkm_id)

    def list(
        self,
        *,
        kategori: KategoriMBKM | None = None,
        status_kegiatan: StatusKegiatan | None = None,
        mitra_id: int | None = None,
    ) -> list[KegiatanMBKM]:
        q = self.db.query(KegiatanMBKMORM)
        if kategori is not None:
            q = q.filter(KegiatanMBKMORM.kategori_mbkm == kategori)
        if status_kegiatan is not None:
            q = q.filter(KegiatanMBKMORM.status_kegiatan == status_kegiatan)
        if mitra_id is not None:
            q = q.filter(KegiatanMBKMORM.mitra_id == mitra_id)
        return [self._to_domain(o) for o in q.order_by(KegiatanMBKMORM.mbkm_id.desc()).all()]

    def get_mbkm_list(
        self,
        *,
        kategori: KategoriMBKM | None = None,
        status_kegiatan: StatusKegiatan | None = None,
        mitra_id: int | None = None,
    ) -> list[KegiatanMBKM]:
        return self.list(
            kategori=kategori,
            status_kegiatan=status_kegiatan,
            mitra_id=mitra_id,
        )

    # ---------- Mutation ----------
    def buat(self, kegiatan: KegiatanMBKM) -> KegiatanMBKM:
        if isinstance(kegiatan, Magang):
            orm: KegiatanMBKMORM = MagangORM(
                mitra_id=kegiatan.mitra_id,
                nama_kegiatan=kegiatan.nama_kegiatan,
                deskripsi=kegiatan.deskripsi,
                kategori_mbkm=KategoriMBKM.MAGANG,
                deadline_pendaftaran=kegiatan.deadline_pendaftaran,
                kuota=kegiatan.kuota,
                status_kegiatan=kegiatan.status_kegiatan,
                tanggal_mulai=kegiatan.tanggal_mulai,
                tanggal_selesai=kegiatan.tanggal_selesai,
                syarat_ketentuan=kegiatan.syarat_ketentuan,
                narahubung=kegiatan.narahubung,
                info_lebih_lanjut=kegiatan.info_lebih_lanjut,
                bidang=kegiatan.bidang,
                posisi=kegiatan.posisi,
                nama_perusahaan=kegiatan.nama_perusahaan,
                logo_url=kegiatan.logo_url,
                penempatan=kegiatan.penempatan,
                kota_lokasi=kegiatan.kota_lokasi,
                alamat_lengkap=kegiatan.alamat_lengkap,
                tipe_gaji=kegiatan.tipe_gaji,
                gaji_perbulan=kegiatan.gaji_perbulan,
                dokumen_dibutuhkan=self._dokumen_to_storage(kegiatan.dokumen_dibutuhkan),
            )
        elif isinstance(kegiatan, Lomba):
            orm = LombaORM(
                mitra_id=kegiatan.mitra_id,
                nama_kegiatan=kegiatan.nama_kegiatan,
                deskripsi=kegiatan.deskripsi,
                kategori_mbkm=KategoriMBKM.LOMBA,
                deadline_pendaftaran=kegiatan.deadline_pendaftaran,
                kuota=kegiatan.kuota,
                status_kegiatan=kegiatan.status_kegiatan,
                tanggal_mulai=kegiatan.tanggal_mulai,
                tanggal_selesai=kegiatan.tanggal_selesai,
                syarat_ketentuan=kegiatan.syarat_ketentuan,
                narahubung=kegiatan.narahubung,
                info_lebih_lanjut=kegiatan.info_lebih_lanjut,
                bidang=kegiatan.bidang,
                tingkat_lomba=kegiatan.tingkat_lomba,
                jenis_peserta=kegiatan.jenis_peserta,
                jumlah_anggota=kegiatan.jumlah_anggota,
                hadiah=kegiatan.hadiah,
            )
        elif isinstance(kegiatan, StudiIndependen):
            orm = StudiIndependenORM(
                mitra_id=kegiatan.mitra_id,
                nama_kegiatan=kegiatan.nama_kegiatan,
                deskripsi=kegiatan.deskripsi,
                kategori_mbkm=KategoriMBKM.STUDI_INDEPENDEN,
                deadline_pendaftaran=kegiatan.deadline_pendaftaran,
                kuota=kegiatan.kuota,
                status_kegiatan=kegiatan.status_kegiatan,
                tanggal_mulai=kegiatan.tanggal_mulai,
                tanggal_selesai=kegiatan.tanggal_selesai,
                syarat_ketentuan=kegiatan.syarat_ketentuan,
                narahubung=kegiatan.narahubung,
                info_lebih_lanjut=kegiatan.info_lebih_lanjut,
                kurikulum=kegiatan.kurikulum,
                metode_pembelajaran=kegiatan.metode_pembelajaran,
                benefit=kegiatan.benefit,
            )
        else:
            raise ValueError(f"Tipe kegiatan tidak dikenali: {type(kegiatan).__name__}")

        self.db.add(orm)
        self.db.flush()
        kegiatan.mbkm_id = orm.mbkm_id
        return kegiatan

    def simpan_perubahan(self, kegiatan: KegiatanMBKM) -> KegiatanMBKM:
        orm = self.db.get(KegiatanMBKMORM, kegiatan.mbkm_id)
        if orm is None:
            raise ValueError(f"Kegiatan id={kegiatan.mbkm_id} tidak ada")

        # update field base
        orm.nama_kegiatan = kegiatan.nama_kegiatan
        orm.deskripsi = kegiatan.deskripsi
        orm.deadline_pendaftaran = kegiatan.deadline_pendaftaran
        orm.kuota = kegiatan.kuota
        orm.status_kegiatan = kegiatan.status_kegiatan
        orm.tanggal_mulai = kegiatan.tanggal_mulai
        orm.tanggal_selesai = kegiatan.tanggal_selesai
        orm.syarat_ketentuan = kegiatan.syarat_ketentuan
        orm.narahubung = kegiatan.narahubung
        orm.info_lebih_lanjut = kegiatan.info_lebih_lanjut

        # update field subclass
        if isinstance(kegiatan, Magang) and isinstance(orm, MagangORM):
            orm.bidang = kegiatan.bidang
            orm.posisi = kegiatan.posisi
            orm.nama_perusahaan = kegiatan.nama_perusahaan
            orm.logo_url = kegiatan.logo_url
            orm.penempatan = kegiatan.penempatan
            orm.kota_lokasi = kegiatan.kota_lokasi
            orm.alamat_lengkap = kegiatan.alamat_lengkap
            orm.tipe_gaji = kegiatan.tipe_gaji
            orm.gaji_perbulan = kegiatan.gaji_perbulan
            orm.dokumen_dibutuhkan = self._dokumen_to_storage(kegiatan.dokumen_dibutuhkan)
        elif isinstance(kegiatan, Lomba) and isinstance(orm, LombaORM):
            orm.bidang = kegiatan.bidang
            orm.tingkat_lomba = kegiatan.tingkat_lomba
            orm.jenis_peserta = kegiatan.jenis_peserta
            orm.jumlah_anggota = kegiatan.jumlah_anggota
            orm.hadiah = kegiatan.hadiah
        elif isinstance(kegiatan, StudiIndependen) and isinstance(orm, StudiIndependenORM):
            orm.kurikulum = kegiatan.kurikulum
            orm.metode_pembelajaran = kegiatan.metode_pembelajaran
            orm.benefit = kegiatan.benefit

        return kegiatan

    def hapus(self, mbkm_id: int) -> None:
        orm = self.db.get(KegiatanMBKMORM, mbkm_id)
        if orm is not None:
            self.db.delete(orm)

    def commit(self) -> None:
        self.db.commit()
