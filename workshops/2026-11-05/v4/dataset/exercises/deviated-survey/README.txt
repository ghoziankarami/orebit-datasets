LATIHAN TAMBAHAN — SURVEY MELENGKUNG (SINTETIS)
Buka project Core baru/salinan; import empat CSV di folder ini.
Tiga lubang dari data utama, kadar/litologi tidak diubah. Survey adalah skenario
sintetis baru:4station per lubang, AZ searah jarum jam dari Utara; DIP positif
ke bawah, vertikal=90°. CRS EPSG:32751, panjang meter, Z elevasi/RL.
Core > Validation > Desurvey memakai Minimum Curvature. Trace station tidak
sama dengan baris assay:Core > Merge menghasilkan XYZ setiap midpoint interval.
output/exercises/reference-results/survey-expected-coordinates.csv memakai integrasi numerik independen tangent slerp
SciPy quad. Toleransi UI/Python:1e-7m, termasuk pembulatan CSV10desimal dan
presisi koordinat UTM. TVD berbeda dari measured depth pada lubang miring.
Latihan ini mengubah posisi:angka solid/tonase baseline vertikal tidak berlaku.
Jangan memasukkannya ke shortcut vertikal notebook utama. Bukan survey nyata.
