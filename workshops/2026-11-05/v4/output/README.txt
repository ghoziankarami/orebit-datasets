CURRENT v4: new simulated Fe/oxides/solid SG. Historical UI comparisons below apply to unchanged Ni/geometry scope only. Read genesis/genesis-method.md. Survey/QAQC exercises are unchanged and remain separate projects.

OUTPUT REFERENSI — BUKAN INPUT AWAL CORE
pair/: solid SAP dari dua surface; loft/: solid SAP dari tiga section.
Kedua footprint berbeda sehingga totalnya tidak boleh dianggap pembanding
akurasi metode estimasi. composites-2m.csv dan block-model-reference.csv adalah
hasil contoh GeoSuite. interpreted-solid.json adalah interpretasi geologi beku,
bukan pengukuran mentah; notebook memakainya untuk menjelaskan clipping/support.
parameters.json menyimpan konfigurasi dan angka acuan dengan source historisnya.
Notebook menghitung ulang bagian numerik yang disebutkan, dan membedakan hasil
hitungnya dari geometri/dukungan blok yang diberikan. Input geologi bukan validasi
geologi independen. File CSV referensi memakai -999 untuk blok tidak diestimasi;
jangan memperlakukannya sebagai kadar Ni negatif nyata.

RINCIAN DATA / PROVENANCE
APAKAH SAMA DENGAN TOMBOL SAMPLE DI GEOSUITE?
Tidak identik. Sample bawaan Core adalah kasus latihan QC dengan tiga masalah
linkage yang didokumentasikan (349 collar/700 survey/8.896 assay/1.368 geology).
Sumber sample yang dikoreksi mempunyai350 collar dan1.372 geology.
Paket workshop ini mempertahankan340 lubang utuh dari sumber sintetis yang sama:
10 lubang tanpa batas bawah SAP yang lengkap dikeluarkan TANPA memilih kadar
atau mengubah pengukuran. Untuk workshop gunakan IMPORT CSV ini, bukan Sample.

GEOLOGI DAN HASIL REFERENSI
LIM dan SAP adalah kode litologi. Domain=interpretasi volume, surface=batas.
Top/Bottom tidak boleh menggabungkan SAP yang terpisah melintasi material/gap.
Pada contoh surface-pair,38 lubang di batas lateral mempunyai468m dukungan
unassigned;302 lubang interior memberi4.122m. Raw340 lubang tetap disimpan.
Density1,6t/m³ adalah asumsi latihan, bukan hasil pengukuran tervalidasi.
Volume mesh berbeda dari volume blok terisi. Hasil ini bukan Mineral Resource
terklasifikasi/patuh SNI/KCMI/JORC dan bukan sign-off Competent Person.

SUMBER & IZIN
Data sintetis, BUKAN endapan nyata. CC BY4.0, kredit Ghozian Karami / Orebit.id.
Sumber: ghoziankarami/orebit-datasets@6b93ac48df79264fda20e4ffc10716280bd2ee8a,
folder02-nikel-laterit. Pengukuran empat CSV identik byte-for-byte dengan paket
workshop v1@46c2958657d7bd437ed90df7f48114e91bb3a5ed; v2 merapikan kemasan.
Lisensi: https://creativecommons.org/licenses/by/4.0/
GeoSuite adalah perangkat lunak GPL-3.0-only; paket dataset bukan rilis aplikasi.

JIKA HASIL BERBEDA
Catat versi app, modepair/loft, parameter, pesan, langkah dan screenshot/proyek.
Ground Fail bukan diperbaiki dengan mengganti batas triangle edge loft atau
menurunkan ring sembarang. Jangan mengubah data supaya sesuai angka referensi.
