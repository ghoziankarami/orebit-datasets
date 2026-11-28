"""Document and package the regenerated workshop v4 folder after its tests.
Run build_workshop_nickel_v4.py, test_workshop_nickel_v4.py, then this script.
"""
from pathlib import Path
import json,hashlib,zipfile
R=Path(__file__).resolve().parents[1];B=R/'workshops/2026-11-05';P=B/'v4'
method='''# Nickel laterite v4 — model kimia untuk pengajaran

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
'''
(P/'output/genesis/genesis-method.md').write_text(method)
(P/'README.txt').write_text('''GEOSUITE WORKSHOP NICKEL v4 — 4–5 November 2026

1. Data utama Core: empat CSV di dataset/. 340collar,680survey,8751assay,1344lithology. Ni/Co dan geometri sama dengan v3; kimia pendamping/SG disimulasikan ulang secara eksplisit dengan anggaran mineral. Baca output/genesis/genesis-method.md.
2. Survey melengkung/Minimum Curvature: empat CSV dataset/exercises/deviated-survey/ pada project baru. 3lubang/12station; oracle64posisi ada di output/exercises/.
3. QA/QC sintetis: dataset/exercises/qaqc-synthetic/qaqc-ni.csv dan sertifikat simulasi pada output/exercises/reference-results/. CRM/blank/duplicate dengan kegagalan disengaja; jangan masuk estimasi.
4. output/ adalah referensi, bukan input yang diunggah bersama empat CSV. Geometri interpretasi dan benchmarkNi historisE7 dipertahankan dalam scopeNi yang tidak berubah; hasil unsur lain tidak diklaim matchedUIE7.
5. Statistik/narasi terbaru, PPT dan notebook disediakan pada paket pengajar Orebit-ops. Versi sumber aplikasi dikonfirmasi instruktur.

Satuan: Ni/Co/Fe %unsur; MgO/SiO2/Al2O3/Cr2O3 %oksida. SG padatan model tanpa dimensi, bukan dry bulk density. Density1.6t/m3 adalah asumsi Resource latihan. Semua data sintetis, CC BY4.0 Ghozian Karami/Orebit.id.
''')
f=P/'output/data-dictionary.md';s=f.read_text().replace('Source specific gravity (dimensionless); measurement/bulk-density representativeness not validated','Modelled solid-mixture relative density (dimensionless); not measured and not dry bulk density');f.write_text(s)
f=P/'output/dataset-provenance.md';s=f.read_text();s='''# Dataset provenance — v4 revision

Geometry, Ni/Co fields and missing mask are retained from the pinned v3 public example. Fe, oxide grades and SG are newly simulated by _generator/build_workshop_nickel_v4.py, seed20261025. These six fields are intentionally different from the historical data described below. The retained UIE7 benchmark/meshes certify the unchanged Ni/geometry calculation scope only. Read genesis/genesis-method.md and verification.json; no new UI parity for all other elements is implied.

## Historical baseline provenance (Ni and geometry)

'''+s;f.write_text(s)
f=P/'output/parameters.json';d=json.loads(f.read_text());d['package_revision']='v4';d['chemistry_revision']='New mineral-budget Fe/oxides/solid SG; Ni/Co/geometry frozen. Historical UI parity scope is Ni only.';f.write_text(json.dumps(d,indent=2)+'\n')
# The original source SHA remains unchanged in retained historical UI files.
version=json.loads((P/'output/genesis/verification.json').read_text());version['generator_sha256']=hashlib.sha256((R/'_generator/build_workshop_nickel_v4.py').read_bytes()).hexdigest();(P/'dataset/VERSION.json').write_text(json.dumps(version,indent=2)+'\n')
f=P/'output/README.txt';s=f.read_text();f.write_text('CURRENT v4: new simulated Fe/oxides/solid SG. Historical UI comparisons below apply to unchanged Ni/geometry scope only. Read genesis/genesis-method.md. Survey/QAQC exercises are unchanged and remain separate projects.\n\n'+s)
lines=[]
for f in sorted(P.rglob('*')):
 if f.is_file() and f.relative_to(P).as_posix()!='output/checksums.sha256':lines.append(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+str(f.relative_to(P)))
(P/'output/checksums.sha256').write_text('\n'.join(lines)+'\n')
Z=B/'GeoSuite_Workshop_Nickel_v4.zip'
with zipfile.ZipFile(Z,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for f in sorted(P.rglob('*')):
  if f.is_file():
   info=zipfile.ZipInfo('GeoSuite_Workshop_Nickel_v4/'+str(f.relative_to(P)),(2026,10,25,0,0,0));info.external_attr=0o100644<<16;info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,f.read_bytes())
with zipfile.ZipFile(Z) as z:assert z.testzip() is None
h=hashlib.sha256(Z.read_bytes()).hexdigest();Z.with_suffix('.zip.sha256').write_text(h+'  '+Z.name+'\n');print('v4 ZIP',Z.stat().st_size,'SHA256',h)
