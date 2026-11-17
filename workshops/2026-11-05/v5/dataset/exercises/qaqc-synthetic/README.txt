LATIHAN TAMBAHAN — QA/QC Ni SINTETIS

Gunakan project Assay terpisah. Upload qaqc-ni.csv, buka Data → QA/QC, lalu
pilih Ni (%). File ini berisi 11 baris: 3 kontrol SIMNI, 2 blank, 3 pasangan
duplikat, dan 3 sampel pembanding biasa.

SIMNI bukan certified reference material komersial. Masukkan mean simulasi
1,00% Ni dan SD 0,04 dari output/exercises/reference-results/qaqc-mock-certificate-and-expected.json.
Z-score hasilnya 0, 2, 5; kontrol terakhir harus dilaporkan gagal pada batas
simulasi 3 SD. Nilai ini hanya latihan, bukan sertifikat laboratorium.

Blank bernilai 0,01% dan 0,08% Ni. Dataset tidak menyertakan DL/LOR yang
dilaporkan laboratorium, sehingga keduanya harus berstatus Not assessed. Nilai
terendah dalam dataset bukan DL/LOR dan tidak boleh dipakai sebagai pengganti.
Untuk menilai blank, peserta perlu memakai DL/LOR resmi yang sesuai metode,
matriks, dan batch laboratorium; bila tidak tersedia, catat keterbatasannya.

HARD duplikat = |asli − duplikat| / (asli + duplikat) × 100. Hasil latihan:
CTRL01 2,4390%, CTRL02 27,2727%, CTRL03 4,7619%; satu pasangan melewati ambang
latihan 20%. Ambang ini bukan batas penerimaan universal.

Latihan ini membuktikan bagaimana aplikasi menampilkan kontrol, bukan kelulusan
QA/QC laboratorium atau mutu deposit. Jangan kirim baris kontrol ke domain,
composite, atau estimasi Resource. Semua nilai dan metadata sintetis, CC BY 4.0
Ghozian Karami/Orebit.id.
