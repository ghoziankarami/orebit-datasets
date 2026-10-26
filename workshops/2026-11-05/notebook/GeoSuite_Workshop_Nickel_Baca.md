# GeoSuite Nickel — Surface pair
**Materi praktis • Ghozian Karami / Orebit.id • Data sintetis 340 lubang**

Baca penjelasan dan grafik dari atas ke bawah. Untuk mengulang perhitungan, jalankan **Run All**; sel per langkah sengaja pendek. Implementasi lengkap tersedia di [engine Python](geosuite_workshop_engine.py). GitHub menampilkan hasil tetapi tidak menjalankan kode.

**Alur:** empat CSV → QC/desurvey → EDA → solid geologi Core → komposit Assay → variogram → block model/NN–IDW–OK → cross-validation → grade–tonnage.

| Pegangan latihan | Nilai |
|---|---|
| Data awal |340 collar / 680 survey / 8.751 assay / 1.344 lithology|
| Koordinat |EPSG:32751; meter; Z elevasi/RL, FROM–TO measured depth|
| Komposit |2 m, SAP; missing bukan nol|
| Density demonstrasi |1,6 t/m³, asumsi eksplisit; bukan SG|
| Tonase baseline pair |21.298.329,56 t pada cutoff 0% Ni|

Notebook memakai empat CSV yang sama dengan UI E7. **Solid dan clipped block support diberikan dari GeoSuite sebagai input geologi bersama.** Python menghitung ulang clipping/komposit dan seluruh estimasi; geometri tidak diklaim sebagai interpretasi independen. Dataset utama ini vertikal; jangan memasukkan survey miring ke shortcut vertikal. Baseline ini belum merupakan laporan sumber daya patuh SNI/KCMI/JORC atau sign-off geolog.

[Versi baca tanpa kode](GeoSuite_Workshop_Nickel_Baca.md) · [Notebook metode lainnya](GeoSuite_Workshop_Nickel_Loft.ipynb)

Pemeriksaan saat ini: 14 sel dijalankan dengan runner Python berurutan, termasuk seluruh assertion baseline. Eksekusi kernel Jupyter/Colab dan peserta/perangkat dicatat terpisah, belum dianggap lulus.


## 0 · Siapkan berkas dan jalankan langkah singkat
Ekstrak paketv2 dan simpan notebook di dekat foldernya. Jika dataset belum ada, sel berikut mengambil paket publik yang **dipatok commit dan SHA-256**, lalu memverifikasinya. Tidak memakai akses privat Codex atau orebit-ops.

[Unduh paket peserta](https://raw.githubusercontent.com/ghoziankarami/orebit-datasets/06b8b3a2efcb963ba446ffc683b2e2552f1a0738/workshops/2026-11-05/GeoSuite_Workshop_Nickel_v2.zip) · [Sumber data asli](https://github.com/ghoziankarami/orebit-datasets/tree/6b93ac48df79264fda20e4ffc10716280bd2ee8a/02-nikel-laterit)

Dependensi yang dipakai saat pemeriksaan: Python3.12, NumPy2.3.5, SciPy1.17.0, pandas2.2.3, matplotlib3.10.8. `requirements.txt` disediakan untuk environment terpisah. Aplikasi GeoSuite sendiri tidak memerlukan Python.


<details>
<summary>Angka hasil langkah ini — buka untuk mencocokkan</summary>

```text
Dataset tersedia. Empat CSV diperiksa pada sel berikutnya.
```

</details>

## 1 · Import empat tabel yang sama
**Tindakan:** jalankan sel, lalu bandingkan nama kolom dengan mapping Core. `MODE='pair'` memakai SAP dari dua surface; `MODE='loft'` memakai interpretasi tiga section. Kedua footprint berbeda.

**Cek:**340collar/680survey/8.751assay/1.344lithology. Jangan memakai tombol Sample bawaan untuk memperoleh angka ini: sample Core adalah latihan QC yang berbeda. Tidak ada pemilihan kadar atau pengubahan nilai pada340lubang ini.


<details>
<summary>Angka hasil langkah ini — buka untuk mencocokkan</summary>

```text
Mode: pair Raw counts: {'collar': 340, 'survey': 680, 'assay': 8751, 'litho': 1344}
```

</details>

## 2 · QC, coordinate system dan log
**Tindakan:** cek ID, interval, missing dan arah dip. X/Y adalah koordinat; ZCOLLAR adalah RL. Untuk lubang vertikal, elevasi pada kedalaman MD adalah `ZCOLLAR−MD`, bukan `MD`.

**Cek:** raw tidak overlap, seluruh ID ada di collar. Raw Ni missing34, bukan34nilai nol. Survey miring ditolak oleh spesialisasi vertikal notebook ini.

**Diskusi:** jika lubang miring, mengapa garis lurus vertikal dan interpolasi station chord tidak cukup?


<details>
<summary>Angka hasil langkah ini — buka untuk mencocokkan</summary>

```text
CRS EPSG:32751; metre; Ni percent. Missing Ni: 34
Raw Ni range: 0.146 3.657
```

</details>

## 3 · EDA sebelum keputusan geologi
**Tindakan:** baca histogram, missing dan peta observasi. Eksplorasi statistik dapat dimulai sebelum solid final.

**Cek:** angka serta unit sesuai tabel raw. Jangan menggunakan klaster/p-value sebagai bukti tunggal tubuh geologi. Jangan mengubah top-cut agar hasilnya sekadar cocok dengan contoh.


![Grafik 1: hasil kalkulasi aktual, interpretasi pair](https://raw.githubusercontent.com/ghoziankarami/orebit-datasets/713332334f153cc14279764af1c4c105fec814ab/workshops/2026-11-05/notebook/figures/pair-readable-01.png)

*Data sintetis workshop, baseline UI E7; grafik perhitungan Python, bukan screenshot aplikasi atau validasi profesional.*

### Baca pola, jangan mengejar korelasi yang bagus
Tujuh unsur/oksida memakai satuan persen; **SG tidak berdimensi**. Bandingkan histogram dan diagram pencar per litologi. Fe–SiO₂ yang berlawanan pada campuran laterit dapat mencerminkan horizon berbeda. Korelasi gabungan bukan alasan otomatis membuat domain atau top-cut. Heatmap SAP membantu membedakan pola dalam satu populasi dari efek pencampuran. Tidak ada kadar yang diubah agar grafik terlihat baik.

<details>
<summary>Angka hasil langkah ini — buka untuk mencocokkan</summary>

```text
Element grades Ni/Co/Fe are elemental mass percent; MgO/SiO2/Al2O3/Cr2O3 are oxide mass percent. SG is dimensionless, not measured dry bulk density.
Missing values remain missing. Histograms are unweighted interval diagnostics; final resource means use supported tonnes.
```

</details>

![Grafik 2: hasil kalkulasi aktual, interpretasi pair](https://raw.githubusercontent.com/ghoziankarami/orebit-datasets/713332334f153cc14279764af1c4c105fec814ab/workshops/2026-11-05/notebook/figures/pair-readable-02.png)

*Data sintetis workshop, baseline UI E7; grafik perhitungan Python, bukan screenshot aplikasi atau validasi profesional.*

![Grafik 3: hasil kalkulasi aktual, interpretasi pair](https://raw.githubusercontent.com/ghoziankarami/orebit-datasets/713332334f153cc14279764af1c4c105fec814ab/workshops/2026-11-05/notebook/figures/pair-readable-03.png)

*Data sintetis workshop, baseline UI E7; grafik perhitungan Python, bukan screenshot aplikasi atau validasi profesional.*

![Grafik 4: hasil kalkulasi aktual, interpretasi pair](https://raw.githubusercontent.com/ghoziankarami/orebit-datasets/713332334f153cc14279764af1c4c105fec814ab/workshops/2026-11-05/notebook/figures/pair-readable-04.png)

*Data sintetis workshop, baseline UI E7; grafik perhitungan Python, bukan screenshot aplikasi atau validasi profesional.*

## 4 · Surface, domain dan solid adalah hal berbeda
**Surface-pair:** SAP memakai Top(SAP) → Bottom(SAP); LIM dapat memakai Top(LIM) → Top(SAP) bila interpretasi log mendukung. **Loft:** ring tertutup pada beberapa section sejajar kemudian dihubungkan.

**Tindakan:** lihat mesh referensi dari perjalanan GeoSuite yang terdokumentasi. Ini adalah keputusan geologi yang diberikan sebagai input, bukan disimpulkan otomatis oleh notebook. Source geometri/hasil historis dipertahankan dalam file referensi; bukan owner acceptance baru.

**Cek:** hash seluruh vertex/face SAP harus sama persis dengan CoreE7; volume serta hash domainLIM juga dicatat bila ada. Hitung volume mesh dengan origin lokal. Whole-mesh volume berbeda dari volume blok terisi dan tonase. Density1,6t/m³ hanyalah asumsi latihan.

**SAP berulang1–4m dan6–7m:** gap4–6m bukan SAP. Kode di bawah menolak beberapa perpotongan vertikal yang belum diinterpretasikan, alih-alih membuat envelope palsu.


<details>
<summary>Angka hasil langkah ini — buka untuk mencocokkan</summary>

```text
PASS exact SAP vertices/faces hash vs native Core: 0200454b7309a491de9ff24bb7757dc601f9d8305e468fccef979ea883116cb2
Same interpreted body: SAP volume 15304948.715316297 m3
Same interpreted body: LIM volume 9120561.31720057 m3
Interpreted SAP whole-mesh volume (not block volume): 15304948.715316301 m³
```

</details>

![Grafik 5: hasil kalkulasi aktual, interpretasi pair](https://raw.githubusercontent.com/ghoziankarami/orebit-datasets/713332334f153cc14279764af1c4c105fec814ab/workshops/2026-11-05/notebook/figures/pair-readable-05.png)

*Data sintetis workshop, baseline UI E7; grafik perhitungan Python, bukan screenshot aplikasi atau validasi profesional.*

## 5 · Constrain raw assay dengan solid
**Tindakan:** gunakan ray/triangle untuk memperoleh interval dukungan dalam mesh. Hole di batas lateral tetap dilaporkan tersendiri, bukan diam-diam dianggap inside.

**Cek pair:**302hole interior dan38hole boundary.4.122m support interior dibanding468m boundary yang tidak otomatis assigned. Semua340rawhole tetap disimpan.

**Diskusi:** boundary policy harus ditetapkan sebelum menjumlah tonase atau menyebut data hilang.


Tabel berikut juga memperlihatkan EDA parent yang dibatasi solid: pair4.122parent/0crossing, loft249parent/32crossing. Mean diagnostik tidak dibobot; dukungan panjang tetap dilaporkan terpisah. Final treatment baseline tetap tanpa cap, sama dengan UI.


<details>
<summary>Angka hasil langkah ini — buka untuk mencocokkan</summary>

```text
Interior holes: 302 Boundary holes excluded explicitly: 38
PASS same domain-constrained parent EDA population/support as UI: 4122 parents; 0 crossing
                        scope  rows  Ni_valid  Ni_missing  mean_unweighted_Ni_pct
                    Raw assay  8751      8717          34                1.313883
SAP reviewed geometry parents  4122      4111          11                1.680841
Final active treatment: none. Geometry parent EDA is diagnostic, not per-span grade treatment or an automatic cap decision.
```

</details>

## 6 · Komposit2m dengan bobot panjang
Rumus: `grade = Σ(length × grade) / Σ(informed length)`; missing tidak menjadi nol. Tail tetap ditampilkan. Input kadar berasal dari **raw assay**, bukan menyalin kadar komposit referensi.

**Cek:** pair2.139composite, loft124composite. Perbandingan ekspor mempertimbangkan presisi depth6desimal dan grade10desimal; bukan toleransi persen universal. Nilai dan dukungan ditulis ke hasil-python/. Handoff derived mean memakai10desimal sesuai kontrak Assay→Resource; ini bukan pembulatan atau pengubahan kadarraw.

**Latihan:** periksa satu komposit secara manual dan bandingkan tail, panjang fisik serta panjang yang memiliki Ni.


<details>
<summary>Angka hasil langkah ini — buka untuk mencocokkan</summary>

```text
Composites: 2139 Physical support: 4122.0 m; missing composite Ni: 1
Max composite grade difference vs GeoSuite export: 3.064215547965432e-14 percentage points
```

</details>

## 7 · Variogram directional dan model yang sama dengan UI
**Tindakan:** hitung EW, NS, vertikal dan omni dengan lag/maxdistance/bins/toleransi yang sama dengan UI. Horizontal memakai jarakXY; vertikal memakai |ΔZ| dengan jarakXY≤5m. Bin=floor(jarak/lag), minimum5pasang/bin dan3bin untuk diterima. Semua jumlah pasangan dan gamma dibandingkan dengan hasil nativeE7. NSloft yang hanya memiliki2bin tetap ditolak, sama dengan UI. Model spherical FINAL memakai nugget/sill/range yang persis sama; saranAutoFit bukan keputusan geologi otomatis.

Geometri komposit presisi penuh menjadi input yang eksplisit dan dibandingkan terhadap koordinat analitik vertikal; beda round-trip harus <1µm. Jangan memakai angka koordinat yang dibulatkan dari screenshot/CSV display untuk benchmark dekat tie tetangga.

**Cek:** nugget/sill/range tercatat; covariance model menggunakan jarak fisik, ellipsoid search mengatur populasi tetangga. Keduanya bukan parameter yang sama.


<details>
<summary>Angka hasil langkah ini — buka untuk mencocokkan</summary>

```text
Applied derived CSV handoff grade precision: ten decimal places; raw grades unchanged
Max geometric round-trip difference (m): 5.684341886080802e-14
EW : PASS 327104 pairs; 10 bins; max gamma difference 0.0
NS : PASS 272981 pairs; 10 bins; max gamma difference 0.0
vert : PASS 7839 pairs; 10 bins; max gamma difference 0.0
omni : PASS 1154035 pairs; 10 bins; max gamma difference 0.0
Same selected final model: {'type': 'spherical', 'nugget': 0.1461, 'sill': 0.2656, 'range': 546.3, 'covarianceMode': 'model-range'}
```

</details>

![Grafik 6: hasil kalkulasi aktual, interpretasi pair](https://raw.githubusercontent.com/ghoziankarami/orebit-datasets/713332334f153cc14279764af1c4c105fec814ab/workshops/2026-11-05/notebook/figures/pair-readable-06.png)

*Data sintetis workshop, baseline UI E7; grafik perhitungan Python, bukan screenshot aplikasi atau validasi profesional.*

## 8 · Block support dan estimasi NN/IDW/OK
**Tindakan:** gunakan support blok terpotong dari interpretasi GeoSuite sebagai input yang dinyatakan jelas. Notebook tidak mengklaim menghitung ulang seluruh clipping volume3D secara independen. Kadar blok referensi hanya dipakai pada sel perbandingan, tidak sebagai input estimasi.

Search baseline:250/250/50m, azimuth0°, dip0°, minimum2 dan maksimum12tetangga, tanpa octant/hole-cap/second-pass. NN memilih satu observasi; IDW memakai jarak fisik berpangkat2; OK menyelesaikan KKT dengan bobot berjumlah1. Stabilizer diagonal1e-9 mengikuti konvensi benchmark yang dinyatakan, bukan menutupi singularitas.

**Cek:** pair2.237blok terestimasi; loft56. Kadar NN/IDW/OK yang disimpan sebagaiFloat32 harus sama persis perblok; hasilDouble tetap ditampilkan untuk auditnumerik. Unknown/-999 pada ekspor bukan kadar negatif yang boleh dirata-ratakan. Lingkungan/model lanjutan di luar konfigurasi ini memerlukan verifikasi tambahan.


<details>
<summary>Angka hasil langkah ini — buka untuk mencocokkan</summary>

```text
Estimated supported blocks: 2237
NN PASS exact stored Float32 parity: 2237 blocks
IDW PASS exact stored Float32 parity: 2237 blocks
OK PASS exact stored Float32 parity: 2237 blocks
PASS kriging variance and neighbour counts; maximum variance difference: 5.053186046266589e-07
```

</details>

## 9 · Bandingkan hasil secara kuantitatif
**Tindakan:** baca max difference, RMSE dan bias; periksa scatterplot, bukan hanya angka total.

Batas perbandingan diturunkan dari penyimpanan grade **Float32**, pembulatan ekspor **6desimal**, serta condition-aware floating-point solver. Tidak ada toleransi persentase generik. Jika assertion gagal, hentikan dan periksa input/config; jangan mengganti parameter supaya hijau.

**Batas validasi:** geometri dan block support diberikan oleh GeoSuite. Agreement di sini memeriksa kalkulasi pada input yang setara, bukan validasi geologi atau review profesional independen. Benchmark pihak ketiga PyKrige yang pernah dilakukan adalah bukti terpisah; notebook ini tidak menjalankannya.


<details>
<summary>Angka hasil langkah ini — buka untuk mencocokkan</summary>

```text
method  blocks  max_abs_percentage_points  RMSE_percentage_points  bias_percentage_points precision_check                                                tolerance_basis
    NN    2237               0.000000e+00            0.000000e+00            0.000000e+00            PASS Float32 half-ULP + six-decimal export half-unit + solver bound
   IDW    2237               5.810293e-07            2.918971e-07            8.299391e-09            PASS Float32 half-ULP + six-decimal export half-unit + solver bound
    OK    2237               6.085750e-07            2.882833e-07            8.430604e-09            PASS Float32 half-ULP + six-decimal export half-unit + solver bound
```

</details>

![Grafik 7: hasil kalkulasi aktual, interpretasi pair](https://raw.githubusercontent.com/ghoziankarami/orebit-datasets/713332334f153cc14279764af1c4c105fec814ab/workshops/2026-11-05/notebook/figures/pair-readable-07.png)

*Data sintetis workshop, baseline UI E7; grafik perhitungan Python, bukan screenshot aplikasi atau validasi profesional.*

## 10 · Cross-validation dengan target dan kebijakan UI yang sama
**Tindakan:** jalankan native-baseline leave-one-observation-out dengan limit200 (pair200observasi, loft124). Seed, target, ellipsoid dan kebijakan top-k/tie sama dengan UI. Pada baseline tanpa hole-cap, UI memilih maksimal12kandidat termasuktarget lalu menghapus target; hingga11tetangga tersisa. Notebook mereproduksi konvensi itu dan menguji setiap daftar tetangga, prediksi dan metric. Ini bukan leave-one-hole-out. Nilai r² adalah korelasiPearson kuadrat sesuai UI, bukan1−SSE/SST.

**Cek:** hasil berulang deterministik dengan input/parameter yang sama. Perubahan MODE membutuhkan Run All. Folder hasil-python/ milik peserta; jangan menimpa raw dataset/.

**Kesimpulan yang boleh disampaikan:** kalkulasi Python pada dataset latihan sudah diuji dengan scope dan batas yang dinyatakan. Bukan bukti semua39layar accepted, bukan uji geolog eksternal, bukan compliant resource statement, dan bukan approval production.


<details>
<summary>Angka hasil langkah ini — buka untuk mencocokkan</summary>

```text
method  valid_pairs     RMSE      bias  source_UI_RMSE result
    NN          200 0.271167  0.096635        0.271167   PASS
   IDW          200 0.226951 -0.002741        0.226951   PASS
    OK          200 0.302314  0.006297        0.302314   PASS
CV r² follows UI squared Pearson correlation; this is not 1-SSE/SST and not drillhole-held-out validation.
```

</details>

![Grafik 8: hasil kalkulasi aktual, interpretasi pair](https://raw.githubusercontent.com/ghoziankarami/orebit-datasets/713332334f153cc14279764af1c4c105fec814ab/workshops/2026-11-05/notebook/figures/pair-readable-08.png)

*Data sintetis workshop, baseline UI E7; grafik perhitungan Python, bukan screenshot aplikasi atau validasi profesional.*

## 11 · Density, cutoff, grade–tonnage dan report
Rumus: `tonnes = supported volume × density`; `contained Ni = tonnes × Ni% /100`. Mean grade harus dibobot tonase.

**Tindakan:** lihat perubahan cutoff0–3%Ni; seluruh kurva tonase/kadar dibandingkan dengan UI, bukan hanya titikakhir. Tonase pada tampilan2desimal wajib sama: pair21.298.329,56t, loft684.068,61t. Perubahancutoff tetap memakai grade tersimpanFloat32 yang sama seperti UI. Mesh seluruh domain, volume terisi, tonase yang diestimasi dan unestimated support harus dibedakan.

**Diskusi:** bagaimana bila density berbeda per litologi? Mengapa kurva ini belum membuktikan RPEEE, klasifikasi atau cadangan?


<details>
<summary>Angka hasil langkah ini — buka untuk mencocokkan</summary>

```text
cutoff_Ni_pct       tonnes  mean_Ni_pct  contained_Ni_t
           0.0 2.129833e+07     1.700600   362199.366079
           0.5 2.129833e+07     1.700600   362199.366079
           1.0 2.128160e+07     1.701153   362032.611476
           1.5 1.565578e+07     1.830722   286613.776737
           2.0 3.273464e+06     2.188679    71645.621817
           2.5 2.051333e+05     2.634977     5405.217277
           3.0 0.000000e+00          NaN        0.000000
Aggregate reconciliation PASS; mean-grade tolerance: 6.886222283436816e-08 percentage points; contained-metal tolerance: 0.01466976766271982 t
FINAL UI / NOTEBOOK CHECK, SAME DOMAIN / SUPPORT / DENSITY / CUTOFF:
               metric       Python     GeoSuite  absolute_difference    tolerance result
Supported volume (m3) 1.331146e+07 1.331146e+07         1.303852e-08 1.000000e-05   PASS
    Final tonnage (t) 2.129833e+07 2.129833e+07         3.352761e-08 1.000000e-04   PASS
          Mean Ni (%) 1.700600e+00 1.700600e+00         3.552714e-15 6.886222e-08   PASS
     Contained Ni (t) 3.621994e+05 3.621994e+05         6.402843e-10 1.466977e-02   PASS
Final tonnage: 21,298,329.56 t; mode=pair; cutoff=0% Ni; density=1.6 t/m3
{
  "mode": "pair",
  "raw_counts": {
    "collar": 340,
    "survey": 680,
    "assay": 8751,
    "litho": 1344
  },
  "mesh_volume_m3": 15304948.715316301,
  "composites": 2139,
  "composite_physical_support_m": 4122.0,
  "estimated_blocks": 2237,
  "supported_volume_m3": 13311455.976011543,
  "tonnes": 21298329.56161847,
  "comparison": [
    {
      "method": "NN",
      "blocks": 2237,
      "max_abs_percentage_points": 0.0,
      "RMSE_percentage_points": 0.0,
      "bias_percentage_points": 0.0,
      "precision_check": "PASS",
      "tolerance_basis": "Float32 half-ULP + six-decimal export half-unit + solver bound"
    },
    {
      "method": "IDW",
      "blocks": 2237,
      "max_abs_percentage_points": 5.810292695862529e-07,
      "RMSE_percentage_points": 2.918970849747557e-07,
      "bias_percentage_points": 8.299390619143419e-09,
      "precision_check": "PASS",
      "tolerance_basis": "Float32 half-ULP + six-decimal export half-unit + solver bound"
    },
    {
      "method": "OK",
      "blocks": 2237,
      "max_abs_percentage_points": 6.085749624240577e-07,
      "RMSE_percentage_points": 2.882833100355162e-07,
      "bias_percentage_points": 8.430604023413877e-09,
      "precision_check": "PASS",
      "tolerance_basis": "Float32 half-ULP + six-decimal export half-unit + solver bound"
    }
  ],
  "CV": [
    {
      "method": "NN",
      "valid_pairs": 200,
      "RMSE": 0.2711670333945482,
      "bias": 0.09663500000000003,
      "source_UI_RMSE": 0.2711670333945482,
      "result": "PASS"
    },
    {
      "method": "IDW",
      "valid_pairs": 200,
      "RMSE": 0.22695143313670652,
      "bias": -0.0027414007420627495,
      "source_UI_RMSE": 0.22695143313670652,
      "result": "PASS"
    },
    {
      "method": "OK",
      "valid_pairs": 200,
      "RMSE": 0.30231382414750335,
      "bias": 0.006296515321265739,
      "source_UI_RMSE": 0.30231382414750346,
      "result": "PASS"
    }
  ],
  "directional": {
    "EW": {
      "lags": [
        25.0,
        75.0,
        125.0,
        175.0,
        225.0,
        275.0,
        325.0,
        375.0,
        425.0,
        475.0
      ],
      "gammas": [
        0.15553344335937525,
        0.16121973486857072,
        0.1673996795126066,
        0.17123371550172448,
        0.1836141923193787,
        0.1839844655009383,
        0.18713407738564578,
        0.1954860400955671,
        0.20179020016753915,
        0.20759954903848793
      ],
      "pairs": [
        8000,
        21875,
        30376,
        33893,
        37025,
        40454,
        40576,
        38402,
        39244,
        37259
      ],
      "totalPairs": 327104
    },
    "NS": {
      "lags": [
        25.0,
        75.0,
        125.0,
        175.0,
        225.0,
        275.0,
        325.0,
        375.0,
        425.0,
        475.0
      ],
      "gammas": [
        0.15881909488341941,
        0.1830622796494957,
        0.19774213289740514,
        0.2373366163560922,
        0.2432162174102673,
        0.27659618480063797,
        0.29981190319977064,
        0.29970984825844404,
        0.27890905590404597,
        0.25187183712485584
      ],
      "pairs": [
        6948,
        16733,
        19231,
        20607,
        28084,
        36166,
        37323,
        38012,
        35590,
        34287
      ],
      "totalPairs": 272981
    },
    "vert": {
      "lags": [
        1.0,
        3.0,
        5.0,
        7.0,
        9.0,
        11.0,
        13.0,
        15.0,
        17.0,
        19.0
      ],
      "gammas": [
        0.03203026916666667,
        0.03841129212179145,
        0.08764073778501635,
        0.1484911864999999,
        0.2117928270408164,
        0.27471741823687734,
        0.3237555267354593,
        0.3613281945945945,
        0.3808347447318008,
        0.4257193487903223
      ],
      "pairs": [
        150,
        1831,
        1535,
        1250,
        980,
        743,
        533,
        370,
        261,
        186
      ],
      "totalPairs": 7839
    },
    "omni": {
      "lags": [
        25.0,
        75.0,
        125.0,
        175.0,
        225.0,
        275.0,
        325.0,
        375.0,
        425.0,
        475.0
      ],
      "gammas": [
        0.1563452225585976,
        0.17271421916876456,
        0.18441760319387934,
        0.20103608690101926,
        0.21206645732995472,
        0.23120163712560324,
        0.24693475161423603,
        0.25597890654046496,
        0.25345613264294703,
        0.2512729663449188
      ],
      "pairs": [
        24361,
        76789,
        95409,
        104783,
        121631,
        140694,
        151078,
        152344,
        146982,
        139964
      ],
      "totalPairs": 1154035
    }
  },
  "limits": [
    "synthetic educational data",
    "vertical survey specialization",
    "shared interpreted mesh and clipped block support; not independent geometry validation",
    "not SNI/KCMI/JORC compliance or professional sign-off",
    "native UI baseline convention reproduced; not all UI options replicated",
    "no raw grades modified"
  ]
}
```

</details>

![Grafik 9: hasil kalkulasi aktual, interpretasi pair](https://raw.githubusercontent.com/ghoziankarami/orebit-datasets/713332334f153cc14279764af1c4c105fec814ab/workshops/2026-11-05/notebook/figures/pair-readable-09.png)

*Data sintetis workshop, baseline UI E7; grafik perhitungan Python, bukan screenshot aplikasi atau validasi profesional.*

### Menjelaskan angka akhir kepada peserta
Bandingkan smoothing NN/IDW/OK pada blok dukungan yang sama. Tonnage dihitung dari **volume dukungan terpotong × dry density 1,6 t/m³**; contained metal memakai Ni/100. Cutoff menaikkan kadar rata-rata dan mengurangi inventory yang disertakan. Grafik ini belum menetapkan reasonable prospects, klasifikasi sumber daya, atau keputusan Competent Person.

<details>
<summary>Angka hasil langkah ini — buka untuk mencocokkan</summary>

```text
Tonnage: sum of clipped support volume × explicit educational dry density 1.6 t/m³. Do not substitute the SG column.
Pair and loft are different interpretations. Shared mesh/support fixes the comparison scope; CP/geological acceptance remains separate.
```

</details>

![Grafik 10: hasil kalkulasi aktual, interpretasi pair](https://raw.githubusercontent.com/ghoziankarami/orebit-datasets/713332334f153cc14279764af1c4c105fec814ab/workshops/2026-11-05/notebook/figures/pair-readable-10.png)

*Data sintetis workshop, baseline UI E7; grafik perhitungan Python, bukan screenshot aplikasi atau validasi profesional.*

![Grafik 11: hasil kalkulasi aktual, interpretasi pair](https://raw.githubusercontent.com/ghoziankarami/orebit-datasets/713332334f153cc14279764af1c4c105fec814ab/workshops/2026-11-05/notebook/figures/pair-readable-11.png)

*Data sintetis workshop, baseline UI E7; grafik perhitungan Python, bukan screenshot aplikasi atau validasi profesional.*

![Grafik 12: hasil kalkulasi aktual, interpretasi pair](https://raw.githubusercontent.com/ghoziankarami/orebit-datasets/713332334f153cc14279764af1c4c105fec814ab/workshops/2026-11-05/notebook/figures/pair-readable-12.png)

*Data sintetis workshop, baseline UI E7; grafik perhitungan Python, bukan screenshot aplikasi atau validasi profesional.*

## Referensi dan tindak lanjut
- Data: Orebit Synthetic Drillhole Datasets, source6b93ac48/02-nikel-laterit; subset340whole-hole, CC BY4.0.
- Konfigurasi dan provenance: output/parameters.json, interpreted-solid.json dan geometry-full-precision.json; source historis dipertahankan.
- CIM2019 MRMR Best Practice: EDA6.2, compositing6.4, density6.5, continuity6.8, model validation6.10; dipakai sebagai konteks metodologi, bukan sertifikasi software.
- JORC2012 Table1 Section3 dan SNI4726:2019 memerlukan konteks/kompetensi pelaporan; tonase dan kadar dari notebook tidak otomatis memenuhi ketentuan tersebut.
- Untuk bug, catat MODE, checksum input, parameter, sel gagal dan pesan. Jangan kirim credential atau data pelanggan.

**Latihan mandiri:** jelaskan pilihan geologi, support yang dikeluarkan, pengaruh komposit, pilihan model/search, dan mengapa total surface-pair tidak boleh dibandingkan langsung dengan loft yang footprint-nya berbeda.

