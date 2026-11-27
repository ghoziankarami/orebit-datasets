# Menggunakan Dataset Open-Pit di Ekosistem Orebit / Using Open-Pit Datasets with Orebit Apps

[Orebit](https://orebit.id/) · [GeoSuite](https://geosuite.orebit.id/) · [PitOpt](https://orebit.id/docs.html) · [Panduan GeoSuite (01–03)](USE_WITH_GEOSUITE.md)

Panduan ini menjelaskan cara mengunduh dan memakai paket data terpadu **`04-emas-open-pit`** (*Gunung Kencana*) dan **`05-nikel-laterit-open-pit`** (*Lamonto*) di seluruh ekosistem aplikasi Orebit: **Orebit GeoSuite**, **Orebit Desktop**, dan **PitOpt**.

> **Peringatan Data Sintetis / Synthetic Disclaimer:** Seluruh data dihasilkan secara deterministik oleh generator di `_generator/` dan **bukan** data tambang atau eksplorasi nyata. Label domain dan kelas (`Measured`, `Indicated`, `Inferred`) adalah atribut model latihan, **bukan** estimasi atau klasifikasi sumber daya/cadangan publik menurut **JORC**, **KCMI**, **SNI**, atau **NI 43-101**.

---

## 1. Unduh Dataset / Download the Datasets

1. Buka repositori `orebit-datasets` di GitHub, klik **Code → Download ZIP** (atau jalankan `git clone https://github.com/ghoziankarami/orebit-datasets.git`), lalu ekstrak.
2. Untuk mengimpor CSV/DXF ke GeoSuite, Orebit Desktop, atau PitOpt, **Python tidak diperlukan**.
3. Pilih **satu** folder proyek open-pit:
   - `04-emas-open-pit/` — endapan stockwork emas–perak **Gunung Kencana** (`EPSG:32748`, UTM 48S, datum vertikal `MSL`)
   - `05-nikel-laterit-open-pit/` — endapan nikel laterit **Lamonto** (`EPSG:32751`, UTM 51S, datum vertikal `MSL`)

| Dataset | Proyek fiktif | CRS & Datum | Lubang bor | Baris assay | Model blok (ukuran sel) | Topografi |
|---|---|---|---:|---:|---|---|
| `04-emas-open-pit` | Gunung Kencana (Au–Ag) | `EPSG:32748`, `MSL` | 104 berarah (19.160,8 m) | 12.669 | 116.056 blok (`15 × 15 × 10 m`) | `surface_topo.dxf` (6.728 segitiga) + `.csv` |
| `05-nikel-laterit-open-pit` | Lamonto (Ni–Co–Fe–MgO–SiO₂) | `EPSG:32751`, `MSL` | 155 vertikal (4.313,0 m) | 4.313 | 28.855 blok (`25 × 25 × 2 m`) | `surface_topo.dxf` (4.200 segitiga) + `.csv` |

---

## 2. Alur Lintas-Aplikasi / Cross-App Workflows

### A. Orebit GeoSuite (`Core → Assay → Resource`)

1. Buka [GeoSuite Core](https://geosuite.orebit.id/try/Core.html), masuk ke tab **Import**, lalu unggah keempat file bor **berheader polos** dari folder yang dipilih: `collar.csv`, `survey.csv`, `assay.csv`, dan `litho.csv`.
2. Verifikasi pemetaan kolom (`BHID`, koordinat meter, `TD`, `AT`/`AZ`/`DIP` konvensi **DIP positif ke bawah**, `FROM`/`TO`, dan kolom kadar).
3. Jalankan validasi & desurvey, ekspor hasil **Core** ke **Assay** untuk komposit dan analisis statistik/domain (`OXIDE`/`TRANS`/`FRESH` atau `OVB`/`LIM`/`SAP`/`BRK`), lalu lanjutkan ke **Resource** untuk pemodelan variogram dan estimasi blok 3D.

### B. Orebit Desktop (Drillholes + Topo DXF + Block Model)

1. Buat proyek baru dengan CRS yang sesuai (`EPSG:32748` untuk `04-emas-open-pit` atau `EPSG:32751` untuk `05-nikel-laterit-open-pit`, satuan meter, elevasi `MSL` positif ke atas).
2. Impor tabel bor (`collar.csv`, `survey.csv`, `assay.csv`, `litho.csv`) — seluruh collar terikat tepat pada permukaan topografi.
3. Impor permukaan topografi `surface_topo.dxf` (layer `TOPOGRAPHY`, `INSUNITS=6` meter) atau fallback `surface_topo.csv`.
4. Muat `block_model.csv` (baris pertama diawali `#` metadata CRS/datum; baris kedua adalah header) untuk membandingkan sampel bor 3D dengan model blok terklasifikasi.

### C. PitOpt (Block Model + Topo DXF)

1. Di PitOpt, muat `block_model.csv` dan atur `surface_topo.dxf` (atau `surface_topo.csv`) sebagai permukaan topografi awal untuk memotong blok udara di atas permukaan (9.715 blok udara pada emas; 1.748 blok udara pada nikel).
2. Tetapkan parameter ekonomi, recovery, dilusi, dan sudut lereng geoteknik secara eksplisit (parameter ekonomi tidak disandikan di CSV), lalu jalankan optimasi pit shell.

---

## 3. Kamus Kolom / Column Dictionary

### Tabel Bor (Header Polos / Plain CSV Headers)

- **`collar.csv`**: `BHID`, `XCOLLAR` (m Easting), `YCOLLAR` (m Northing), `ZCOLLAR` (m RL, MSL), `TD` (m total depth)
- **`survey.csv`**: `BHID`, `AT` (m downhole), `AZ` (derajat 0–360), `DIP` (derajat 0–90, **positif ke bawah**; 90 = vertikal turun)
- **`assay.csv` (`04-emas-open-pit`)**: `BHID`, `FROM`, `TO` (m), `AU_GPT` (g/t), `AG_GPT` (g/t), `SG` (t/m³)
- **`assay.csv` (`05-nikel-laterit-open-pit`)**: `BHID`, `FROM`, `TO` (m), `NI_PCT` (%), `CO_PCT` (%), `FE_PCT` (%), `MGO_PCT` (%), `SIO2_PCT` (%), `SG` (t/m³)
- **`litho.csv` (`04-emas-open-pit`)**: `BHID`, `FROM`, `TO` (m), `LITH` (`OXIDE`, `TRANS`, `FRESH`), `ALT` (`SIL`, `ARG`, `PROP`)
- **`litho.csv` (`05-nikel-laterit-open-pit`)**: `BHID`, `FROM`, `TO` (m), `LITH` (`OVB`, `LIM`, `SAP`, `BRK`)

### Model Blok & Topografi

- **`block_model.csv`** *(baris 1 diawali `#` metadata CRS & datum)*:
  `X`, `Y`, `Z` (m pusat sel, Z positif ke atas), `DX`, `DY`, `DZ` (m ukuran sel), `DENSITY` (t/m³), `DOMAIN`, `CLASS` (`Measured`, `Indicated`, `Inferred`), serta kolom kadar (`AU_GPT`, `AG_GPT` atau `NI_PCT`, `CO_PCT`, `FE_PCT`, `MGO_PCT`, `SIO2_PCT`).
- **`surface_topo.csv`** *(baris 1 diawali `#` metadata)*: `X`, `Y`, `Z` (m).
- **`surface_topo.dxf`**: ASCII DXF R12 `3DFACE` pada layer `TOPOGRAPHY`, `$INSUNITS = 6` (meter).

---

## 4. English Summary

1. Download the repository ZIP (or `git clone`) and choose either `04-emas-open-pit` (**Gunung Kencana**, `EPSG:32748`, MSL) or `05-nikel-laterit-open-pit` (**Lamonto**, `EPSG:32751`, MSL). No Python is needed to import the CSVs or DXF files.
2. **Orebit GeoSuite**: Import the four plain-header drillhole tables (`collar.csv`, `survey.csv`, `assay.csv`, `litho.csv`) into `Core` using positive-down `DIP`, then pass outputs through `Assay` compositing and `Resource` estimation.
3. **Orebit Desktop**: Load the drillholes alongside `surface_topo.dxf` (or `.csv`) and `block_model.csv` in the matching UTM zone (`EPSG:32748` / `EPSG:32751`, MSL) to inspect 3D spatial coherency between drillhole intercepts, topography, and block grades.
4. **PitOpt**: Load `block_model.csv` and clip air blocks against `surface_topo.dxf` (or `.csv`), then supply explicit economic and slope parameters to run pit optimisation.
5. **Synthetic Notice**: All figures are generated deterministically for education, tutorials, and software testing. They are **not** real exploration data and **must not** be used to support public resource or reserve reporting under JORC, KCMI, SNI, or NI 43-101.
