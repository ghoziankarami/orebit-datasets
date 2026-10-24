# Workshop GeoSuite Nickel — 4–5 November 2026

Mulai dengan [paket peserta v2.1](GeoSuite_Workshop_Nickel_v2.zip?raw=true), ekstrak, lalu baca **README.txt**. Isi paling atas hanya README.txt, dataset/ dan output/. Empat CSV pada dataset/ adalah input awal Core; output/ adalah referensi, bukan file yang diunggah bersama input.

**Jalur utama:** peserta mengimpor sendiri empat CSV workshop, mengikuti demonstrasi dan PPT. **Jalur pendamping:** [baca notebook Python beserta hasilnya di GitHub](notebook/GeoSuite_Workshop_Nickel.ipynb); jalankan melalui Jupyter atau Colab dengan dependensi yang disebutkan notebook. GitHub menampilkan notebook, bukan menjalankan kernel. Notebook menggunakan raw data yang sama; geometri interpretasi dan clipped block support diberikan sebagai input yang dinyatakan jelas, bukan validasi geologi independen.

Paket ini adalah subset340lubang utuh dari data sintetis6b93ac48/02-nikel-laterit:340collar,680survey,8751assay,1344lithology. Nilai pengukuran identik dengan paketv1. Sepuluh lubang tanpa logged SAP base lengkap dikeluarkan tanpa pemilihan kadar. Missing tetap missing. Data bukan endapan nyata. CC BY4.0, kredit Ghozian Karami/Orebit.id.

Tombol Sample bawaan Core berbeda: ia adalah latihan validasi dengan tiga masalah linkage yang disengaja. Gunakan empat CSV workshop untuk alur pelatihan; jangan mencampur jumlah/hasil sample bawaan dan paket340ini. Surface-pair dan loft memakai footprint berbeda; bukan perbandingan tonase langsung.38boundaryholes/468m pada pair tetap unassigned secara eksplisit; raw340lubang dipertahankan.

[Paketv1 terdahulu](https://github.com/ghoziankarami/orebit-datasets/blob/46c2958657d7bd437ed90df7f48114e91bb3a5ed/workshops/2026-11-05/participant-training-package.zip) tetap utuh untuk mereproduksi bukti lama. Paket dataset/notebook bukan rilis aplikasi, sign-off profesional, acceptance39layar atau approval production. Akses aplikasi/versi dikonfirmasi instruktur secara terpisah.

Revisiv2.1 menambah kontrak dan hasil UIE7 untuk hash seluruh solid, variogram directional, model/search, seluruh gradeblokFloat32, LOOdan seluruh cutoff. Empat CSV pengukuran tidak berubah. Versi tepat harus tetap dicatat ketika mereview UI.
