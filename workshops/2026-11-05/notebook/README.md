# Notebook Python pendamping GeoSuite

[Buka notebook dan hasilnya](GeoSuite_Workshop_Nickel.ipynb). Ini memakai **empat CSV340lubang yang sama** dengan paket workshop, bukan tombol Sample bawaan Core.

## Cara menggunakan

1. Untuk membaca, buka `.ipynb` di GitHub: kode, tabel dan grafik sudah terisi.
2. Untuk menjalankan, unduh notebook lewat **Download raw file**. Buka dengan Jupyter yang tersedia, atau Colab → **File → Upload notebook**. GitHub sendiri bukan kernel interaktif.
3. Jalankan **Run All**. Dataset lokal yang sudah diekstrak diperiksa checksum-nya. Bila belum ada, sel pertama mengunduh paket publik yang dipatok commit/hash; tidak memakai akses orebit-ops privat.
4. Mulai dengan `MODE='pair'`. Untuk interpretasi loft, ubah menjadi `MODE='loft'` dan jalankan ulang semua sel dari lingkungan bersih. Jangan membandingkan total kedua footprint sebagai bias metode.
5. Hasil sendiri disimpan pada `hasil-python/`; input `dataset/` tidak ditimpa.

Untuk environment Python terpisah, gunakan Python3.12 dan dependensi pada `requirements.txt`. Jupyter/Colab frontend yang sah tetap diperlukan. Tidak ada instalasi otomatis ke environment global dalam notebook.

## Yang benar-benar diperiksa

- Dua mode, masing-masing12sel kode, dieksekusi berurutan dengan Python3.12/NumPy2.3.5/SciPy1.17.0/pandas2.2.3/matplotlib3.10.8: **PASS**. Format JSON notebook divalidasi terhadap schema resmi nbformat4.
- Raw input dan checksum tetap; compositepair2139/loft124; supportpair4122m/loft232.26051110387328m.
- Perbandingan NN/IDW/OK: pair2237blok dan loft56blok. Max grade difference keseluruhan6.085749633122362e-7percentagepoints; batas berasal dari half-ULPFloat32 + pembulatan ekspor6desimal + condition-aware solver, bukan persen toleransi arbitrer.
- Whole-mesh/supportvolume/tonase, mean grade dan containedmetal direkonsiliasi pada scope yang sama. Plot memakai hasil perhitungan aktual.
- **Ini pemeriksaan sel dengan runner Python, bukan klaim eksekusi kernel Jupyter/Colab atau uji peserta/perangkat.** Verifikasi kernel pada cloud masih menunggu izin instalasi environment sementara. Ini tidak menghalangi membaca kode/hasil di GitHub; konfirmasi jalur Jupyter peserta sebelum menjadikannya fallback acara.

## Batas ilmiah

Interpretasi solid, koordinat geometri presisi penuh dan clipped block support diberikan dari reference GeoSuite. Python menghitung clipping raw, komposit dan estimasi; ia tidak membuktikan ulang seluruh geometri/tinjauan geologi. Survey contoh vertikal; spesialisasi ini menolak survey miring. Variogram Python omnidirectional; contoh LOO30observasi bukan leave-one-hole-out atau semua konfigurasi UI.

CSV display membulatkan koordinat: memakai angka tersebut untuk benchmark dapat mengubah pilihan12tetangga dekat tie. File `geometry-full-precision.json` mempertahankan input geometri asli yang dinyatakan jelas; parameter/kadar tidak diubah agar cocok.

Tidak ada klaim sign-off CP, compliance SNI/KCMI/JORC, owner acceptance39layar, deployment, atau validasi profesional independen. Data/kode pendidikan ini CC BY4.0 dengan kredit Ghozian Karami/Orebit.id; source aplikasi GeoSuite mempunyai lisensinya sendiri.

## Tonase akhir wajib sama dengan UI

Perbandingan langsung dengan ekspor perjalanan UI asli **GeoSuite e7f79300**, dataset340dan parameter sama (density1,6t/m³, cutoff0%Ni):

| Interpretasi | Blok terestimasi | Tonase UI | Tonase Python | Selisih |
|---|---:|---:|---:|---:|
| Surface-pair |2237|21.298.329,56t|21.298.329,56t|0t|
| Loft |56|684.068,61t|684.068,61t|0t|

Selisih nol juga terukur pada nilai double dari CSVnative, sebelum pembulatan tabel ini. Assertion notebook juga meminta nilai yang ditampilkan2desimal sama. Dukungan blok memang diberikan dari GeoSuite; tabel ini tidak mengklaim validasi clipping geometri independen. Ini bukan bukti bahwa build publik yang berbeda di orebit.id sudah sama; versi/dataset/parameter UI harus dikonfirmasi.

[Notebook loft dengan hasil terisi](GeoSuite_Workshop_Nickel_Loft.ipynb) tersedia bila ingin membaca interpretasi alternatif tanpa menjalankan ulang modepair. Grafik yang tertanam sebagai tautan PNG adalah hasil perhitungan aktual, bukan screenshotUI atau gambarAI. Verifikasi live staging/owner acceptance tetap terpisah; pembaruan staging sedang ditahan untuk review.
