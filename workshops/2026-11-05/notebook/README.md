# Notebook pendamping GeoSuite — baseline yang sama dengan UI

[Buka surface-pair](GeoSuite_Workshop_Nickel.ipynb) · [Buka loft](GeoSuite_Workshop_Nickel_Loft.ipynb). GitHub menampilkan kode, tabel dan grafik aktual; untuk menjalankan, unduh `.ipynb`, buka di Jupyter yang tersedia atau Colab → File → Upload notebook, lalu **Run All**.

Notebook memakai **empat CSV untuk 340 lubang yang sama dengan demonstrasi**, bukan tombol Sample Core. Sel pertama memakai paket publik yang dipatok commit/hash; tidak perlu akses orebit-ops privat. Input dataset/ tidak ditimpa; hasil sendiri tersimpan di hasil-python/. Python 3.12 dan requirements.txt adalah baseline pemeriksaan. GeoSuite browser tidak memerlukan Python.

## Yang sekarang harus sama

Perbandingan untuk setiap metode adalah **GeoSuite E7 ↔ Python**, bukan memaksa surface-pair dan loft mempunyai footprint sama.

| Kontrak baseline | Pemeriksaan |
|---|---|
| Empat CSVraw |Checksum identik;340 collar / 680 survey / 8.751 assay / 1.344 lithology|
| Solid SAP |Seluruh vertex/face dan hash sama persis dengan Core E7; pair: 680 vertex / 1.356 face, loft: 111 vertex / 218 face|
| Domain LIM konteks pair |Volume/hash dari Core yang sama dicatat; Resource baseline tetap SAP|
| EDA dalam domain | Pair 4.122 parent / 0 crossing; loft 249 parent / 32 crossing; dukungan serta mean diagnostik tanpa bobot dilaporkan terpisah |
| Komposit 2 m |Pair 2.139, loft 124; dihitung dari raw, boundary support/missing tetap eksplisit|
| Handoff |Derived mean pada 10 desimal sesuai kontrak Assay→Resource; tidak membulatkan/mengubah kadar mentah|
| Variogram EW / NS / vertikal / omni |Lag/bins/maxdistance/toleransi, jumlah pasangan dan gamma dibandingkan dengan UI. NS pada loft: 2 bin / 508 pasangan ditolak sama seperti UI|
| Model final |Pair spherical: `nugget=0.1461`, `sill=0.2656`, `range=546.3 m`. Loft spherical:`nugget=0.1621`, `sill=0.4052`, `range=56.3 m`. SaranAutoFit tidak otomatis menjadi keputusan geologi|
| Search |250/250/50m, azimuth 0°, dip 0°,min 2, max 12, tanpa octant/holecap/secondpass; semua applied fields diperiksa|
| Grade blokNN/IDW/OK |Kadar tersimpanFloat32 harus sama persis pada 2.237 blok pair dan 56 blok loft; hitunganDouble juga diaudit|
| Kriging variance / jumlah tetangga | KRIGE_VAR cocok dengan presisi ekspor UI; jumlah tetangga per blok sama persis |
| Cross-Val |Targetseed dan kebijakan neighbour/tie native sama:200 observasi pair / 124 loft; semua prediksi/metric dibandingkan|
| Grade–tonnage |Seluruh cutoff 0–3% Ni dibandingkan, memakai gradeFloat32 dan scope/density yang sama|

## Tonase akhir wajib sama

Hasil dibandingkan dengan ekspor perjalanan UI asli **GeoSuite e7f79300**, density 1,6 t/m³, cutoff 0% Ni, SAP dan dukungan blok yang sama:

| Interpretasi | TonaseUI | TonasePython |
|---|---:|---:|
| Surface-pair |21.298.329,56t|21.298.329,56t|
| Loft |684.068,61t|684.068,61t|

Assertion meminta kesamaan angka tampilan2desimal, rekonsiliasi volume/massa/mean/metal, serta seluruh kurva cutoff. Toleransi kalkulasi mengikuti Float32/exportprecision/condition-aware solver dan presisi agregasi, bukan persentase arbitrer.

## Cara membaca hasil dan batasnya

Setiap notebook mempunyai12 sel kode yang diperiksa berurutan, tabel hasil terisi dan grafikPNG dari kalkulasi nyata. FormatJSON divalidasi terhadap schema resmi nbformat4. Grafik ditautkan sebagai filePNG agar artefak mudah diperiksa tanpa encodedimage besar; saat menjalankan kernel, grafik baru juga muncul dari kode. Gambar ini bukan screenshotUI atau AI.

**Pemeriksaan ini menggunakan runnerPython berurutan; eksekusi kernel Jupyter/Colab di cloud belum diverifikasi karena izin instalasi sementara masih pending.** Jangan menyebutnya uji peserta/perangkat. Membaca hasil di GitHub tidak memerlukan instalasi. Konfirmasi jalur kernel peserta sebelum menjadikannya fallback acara.

Interpretasi solid dan clipped block support diberikan sebagai input dari GeoSuite; ini membuktikan kesetaraan input/hasil baseline, **bukan rekonstruksi geologi independen**. Survey contoh vertikal; notebook menolak data miring. Final scalar model yang sama tidak otomatis cocok untuk setiap arah; perbedaan kontinuitas vertikal tetap bahan interpretasi, bukan ditutupi dengan mengganti parameter.

KonvensiCV native baseline tanpa hole-cap memilih hingga 12 kandidat termasuktarget, lalu menghapusself; bisa tersisa11 neighbour. Notebook mengikuti konvensi ini, bukan menganggap semua desainCV ekuivalen. r² mengikuti korelasiPearson kuadrat UI, bukan1−SSE/SST; bukan leave-one-hole-out.

Ini tidak mengklaim semua opsiUI / 39 layar telah direplikasi/accepted, sign-off geolog/CP, complianceSNI / KCMI / JORC, atau kesamaan dengan build publik yang berbeda. Source/version/dataset/parameter UI harus dicatat. Staging sedang ditahan untuk review pemilik; notebook bukan approval deployment.

Data/kode pendidikan: CC BY4.0, kredit Ghozian Karami/Orebit.id; source aplikasi GeoSuite mempunyai lisensi sendiri. Konfigurasi/provenance dan referensi metode tersimpan pada output/ paket. Gunakan salinan eksperimen untuk parameter lain dan jangan menyebut hasilnya matched tanpa perbandingan baru.
