LATIHAN TAMBAHAN — QA/QC Ni SINTETIS
Gunakan project Assay baru/salinan. Upload qaqc-ni.csv, buka QA/QC, pilih Ni(%).
SIMNI adalah kontrol simulasi, BUKAN certified material komersial. Masukkan
mean1.00 dan SD0.04 ke grupSIMNI dari output/exercises/reference-results/qaqc-mock-certificate-and-expected.json.
Z=(hasil-mean)/SD:0,2,5;hasil terakhir gagal aturan>3SD. BLANK-02=8×DL proxy
ditandai; BLANK-01=1×. UI memakai minimum nilai positif sebagai proxy DL;
contoh sengaja memiliki minimum.01%, sama dengan angka latihan, bukan impor
DL laboratorium. Untuk pekerjaan nyata gunakan certificate/LOR resmi dan
protokol lab; fitur proxy ini tidak membuktikan kelulusan batch laboratorium.
Duplikat: HARD=abs(a-b)/(a+b)*100;CTRL02 pasangan2.0/3.5 gagal ambang20%.
Ketidakpastian dekatLOR perlu evaluasi terpisah, bukan ambang universal.
Data kontrol ini tidak boleh dikirim untuk domain/composite/resource estimation.
Semua nilai dan metadata sintetik, CC BY4.0 Ghozian Karami/Orebit.id.
