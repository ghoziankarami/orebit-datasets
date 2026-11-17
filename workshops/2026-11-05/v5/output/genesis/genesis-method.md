# Nickel laterite v4 — model kimia untuk pengajaran

V4 adalah simulasi baru yang dinyatakan terang, bukan koreksi otomatis pengukuran lapangan. Geometri, interval, Ni, Co dan 34 missing dipertahankan dari v3 agar benchmark Ni dapat diperiksa kembali. Fe, MgO, SiO2, Al2O3, Cr2O3 dan SG disimulasikan ulang dari anggaran komponen mineral.

## Model genesa yang dipilih

Contoh ini mewakili profil laterit silikat di atas ultramafik: tudung ferruginous/OVB → LIM kaya goethite → SAP lebih kaya Mg-silikat → BRK sebagian terserpentinisasi. Ini satu skenario pendidikan; bukan seluruh tipe laterit, bukan endapan nyata dan bukan model kalibrasi untuk Sulawesi/Halmahera. Smectite transition tidak dimodelkan; horizon Co pada kontak LIM/SAP adalah pola sintetis yang diwarisi, bukan bukti adanya mineral Mn tertentu.

Komponen memakai stoikiometri endmember goethite, hematite, serpentine/lizardite, forsterite, enstatite, quartz, gibbsite, chromite, magnetite dan minor spinel. Proporsi ujung horizon dan variasi compositional seed20261025 merupakan pilihan desain yang tersimpan pada generator. Setiap unit massa komponen berjumlah100% sebelum pembulatan. NiO/CoO adalah ekuivalen pembukuan untuk trace substitution/hosts, bukan klaim fase NiO/CoO bebas yang ditemukan oleh XRD. Proporsi ini tidak diklaim sebagai mineralogi terukur, equilibrium speciation, recovery metalurgi atau pelapukan bermassa-konservasi dari satu blok batuan induk.

`component-budget.csv` memuat FeO dan Fe2O3 terpisah, oksida lain, H2O struktural model, proporsi host dan closure. Fe pada assay tetap persen unsur total; jangan menjumlah Fe unsur dengan FeO/Fe2O3 yang mewakilinya. LOI/H2O model bukan hasil furnace atau moisture assay; tidak dipakai sebagai dry/wet correction terhadap data lapangan. Komposisi mentah tidak dipaksa sum100; yang berjumlah100 adalah anggaran generatif yang lengkap dan diungkap.

SG adalah **relative density padatan sintetis** dari reciprocal-volume mixing nominal endmembers, tanpa pori/free water. Nominalrho g/cm³: goethite4.28,hematite5.26,serpentine2.55,forsterite3.275,enstatite3.20,quartz2.65,gibbsite2.40,chromite4.65,magnetite5.18,spinel3.58. Trace-equivalent density6.67/6.44 adalah asumsi kecil model. SG tidak sama dengan dry bulk density. Resource tetap memakai asumsi latihan1.6t/m³ yang eksplisit, tidak mengubah SG menjadi bulk density.

## Verifikasi dan batasnya

- Ni/Co, missing mask, collar/survey/litho dan interval tetap identik dengan v3. Ini mempertahankan **scope benchmark Ni**, bukan kesamaan seluruh kimia dengan UIE7.
- Nol baris complete dengan jumlah parsial reported mass percentages >100. Anggaran seluruh komponen100 dalam presisi numerik; totalFe CSV diverifikasi terhadap FeO/Fe2O3 model secara independen.
- Mean Ni SAP>LIM>BRK; Co LIM>SAP>BRK; Fe LIM>SAP>BRK; MgO BRK>SAP>LIM; SiO2 SAP>LIM pada skenario ini. Ini target generatif, bukan batas penerimaan universal atau sertifikasi lapangan.
- Mutasi penghilangan host budget membuat pemeriksaan gagal. Datasetv3 dan daftar10flag sebelumnya tetap dipertahankan sebagai riwayat/latihan diagnosis.
- Mean deposit USGS tidak dipakai sebagai cutoff penolakan satu interval. Korelasi, CV dan cluster tidak memberi geological approval otomatis.

## Rujukan primer

USGS2013 memberi model genesa umum; formula/density endmember dirujuk dari Handbook of Mineralogy. Proporsi campuran dan tracebudget adalah asumsi generator ini, bukan angka rekomendasi dari rujukan.

- https://www.usgs.gov/publications/nickel-cobalt-laterites-a-deposit-model
- https://handbookofmineralogy.org/pdfs/goethite.pdf
- https://handbookofmineralogy.org/pdfs/lizardite.pdf
- https://handbookofmineralogy.org/pdfs/forsterite.pdf
- https://handbookofmineralogy.org/pdfs/enstatite.pdf
- https://handbookofmineralogy.org/pdfs/chromite.pdf
- https://handbookofmineralogy.org/pdfs/gibbsite.pdf
- https://handbookofmineralogy.org/pdfs/hematite.pdf
- https://handbookofmineralogy.org/pdfs/magnetite.pdf

Data dan generator pendidikan CC BY4.0, kredit Ghozian Karami/Orebit.id. Ini bukan laporan Mineral Resource, validasi laboratorium, signoff CP atau penerimaan semua fitur aplikasi.
