"""Package unchanged v4 chemistry plus explicit validation/geometry exercises."""
import csv
import hashlib
import io
import json
from pathlib import Path
import zipfile

BASE = Path(__file__).resolve().parents[1] / 'workshops/2026-11-05'
V4 = BASE / 'v4'
OUT = BASE / 'v5'
files = {}
for folder in ['dataset', 'output/genesis', 'output/exercises/reference-results']:
    for path in sorted((V4 / folder).rglob('*')):
        if path.is_file():
            files[path.relative_to(V4).as_posix()] = path.read_bytes()
for name in ['output/data-dictionary.md', 'output/dataset-provenance.md', 'output/exercises/exercise_reference.py']:
    files[name] = (V4 / name).read_bytes()


def csv_bytes(headers, rows):
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode()


tables = {}
for name in ['collar', 'survey', 'assay', 'litho']:
    reader = csv.DictReader(io.StringIO(files[f'dataset/{name}.csv'].decode()))
    tables[name] = (reader.fieldnames, list(reader))
holes = {r['BHID'] for r in tables['collar'][1][:4]}
clean = {name: [dict(r) for r in rows if r['BHID'] in holes] for name, (_, rows) in tables.items()}
faulty = json.loads(json.dumps(clean))
faults = []


def edit(table, index, column, value, purpose):
    old = faulty[table][index][column]
    faulty[table][index][column] = value
    faults.append(dict(file=table + '.csv', csv_row=index + 2, column=column,
                       faulty=value, corrected=old, action='edit', purpose=purpose))


edit('collar', 1, 'XCOLLAR', '', 'Missing X must not become an origin point.')
faulty['collar'].append(dict(faulty['collar'][0]))
faults.append(dict(file='collar.csv', csv_row=len(faulty['collar']) + 1,
                   action='delete', purpose='Duplicate collar ID; keep the original source row.'))
edit('survey', 4, 'AZ', '400', 'Out-of-range azimuth must quarantine the trace.')
edit('survey', 7, 'DIP', '110', 'Invalid dip must remain raw and block geometry.')
edit('assay', 1, 'FROM', '0.5', 'Overlap must be fixed from the known synthetic source.')
edit('assay', len(faulty['assay']) - 1, 'BHID', 'ORPHAN-TRAINING', 'Mistyped ID must be linked to the source record.')
for table, (headers, _) in tables.items():
    files[f'dataset/exercises/validation/input/{table}.csv'] = csv_bytes(headers, faulty[table])
    files[f'output/exercises/validation-answer/{table}.csv'] = csv_bytes(headers, clean[table])
files['output/exercises/validation-answer/answer-key.json'] = (json.dumps({
    'synthetic': True, 'base': 'orebit-datasets c4c65e5 v4', 'faults': faults,
    'expected_clean_rows': {key: len(value) for key, value in clean.items()},
    'rules': ['Exactly six injected source defects; the UI may group them into fewer findings.',
              'Answer files are the retained synthetic source, never inferred field measurements.',
              'Revalidate after Apply or corrected CSV reimport; do not skip failed holes to claim a clean repair.']
}, indent=2) + '\n').encode()

# A deliberately simple analytical geometry example, distinct from full v4 chemistry.
headers = {'collar': ['BHID', 'XCOLLAR', 'YCOLLAR', 'ZCOLLAR', 'TD'],
           'survey': ['BHID', 'AT', 'AZ', 'DIP'],
           'assay': ['BHID', 'FROM', 'TO', 'NI_PCT'],
           'litho': ['BHID', 'FROM', 'TO', 'LITH']}
geometry = {name: [] for name in headers}
for i in range(6):
    for j in range(6):
        hole, depth = f'G{i}{j}', 4 + i + j / 2
        geometry['collar'].append(dict(zip(headers['collar'], [hole, 700000 + 20*i, 9800000 + 20*j, 100, depth + 10])))
        for md in [0, depth + 10]:
            geometry['survey'].append(dict(zip(headers['survey'], [hole, md, 0, 90])))
        for start, end, code, grade in [(0, depth, 'LIM', .9), (depth, depth+6, 'SAP', 1+i/10+j/50), (depth+6, depth+10, 'BRK', .2)]:
            geometry['assay'].append(dict(zip(headers['assay'], [hole, start, end, grade])))
            geometry['litho'].append(dict(zip(headers['litho'], [hole, start, end, code])))
for name in headers:
    files[f'dataset/exercises/domain-known-answer/{name}.csv'] = csv_bytes(headers[name], geometry[name])
files['output/exercises/domain-known-answer.json'] = (json.dumps({
    'purpose': 'Synthetic analytical Surface/Loft geometry exercise; Ni-only, not a multielement genesis model.',
    'crs': 'EPSG:32748', 'dip': 'positive down', 'collars': 36, 'survey_stations': 72,
    'assay_rows': 108, 'sap_solid_m3': 100*100*6, 'sap_thickness_m': 6,
    'independent_coordinates': 'X/Y equal collar; Z=100-measured depth for these vertical traces.',
    'loft_world_sections': [
        {'northing': 9800000, 'ring': [[700000, 96], [700100, 91], [700100, 85], [700000, 90]]},
        {'northing': 9800100, 'ring': [[700000, 93.5], [700100, 88.5], [700100, 82.5], [700000, 87.5]]}],
    'density': 'No measured density supplied; any Resource density is a separately recorded training assumption.',
    'boundary_note': 'Twenty hull holes lie on lateral boundaries. Inspect measured membership and the explicit boundary policy; never assume all36holes are strict interior samples.',
    'limits': '60000m3 proves geometry only; model support, estimated mass and confidence require separate checks.'
}, indent=2) + '\n').encode()

files['README.txt'] = '''GEOSUITE WORKSHOP NICKEL v5 â€” START HERE

Use a NEW PROJECT for each scenario. Never upload output/ or mix scenarios.

1 VALIDATION AND REPAIR
  Upload the four CSVs in dataset/exercises/validation/input/.
  Six source defects are intentional: missing X, duplicate collar, invalid azimuth,
  invalid dip, overlapping assay and mistyped hole ID. Locate exact rows in Core.
  For the retained source values and corrected reimport use output/exercises/validation-answer/.
  A green result after excluding faulty holes is not a completed repair.

2 MINIMUM CURVATURE
  Upload the four CSVs in dataset/exercises/deviated-survey/.
  Three holes,12survey stations; independent64-position references remain in
  output/exercises/reference-results/. Read the scenario README before importing.

3 DOMAIN -> ASSAY -> RESOURCE
  Simple Surface/Loft exercise: dataset/exercises/domain-known-answer/.
  CRS EPSG32748;36collars,72survey,108assays. SAP thickness6m and closed volume60000m3.
  World section corners and limitations: output/exercises/domain-known-answer.json.
  Full nickel laterite exercise: the four CSVs directly in dataset/ (EPSG32751).
  These340collar/680survey/8751assay/1344lithology rows and all chemical values
  are byte-identical to v4. Read output/genesis/genesis-method.md and the data dictionary.
  Geological interpretation, boundary decisions, actual filled support and density
  require separate explicit reviews; a successful UI action is not a geological signoff.

4 QA/QC â€” SEPARATE CONTROL DATA
  dataset/exercises/qaqc-synthetic/qaqc-ni.csv is for the Assay QAQC tool.
  Certificates/expected failures are simulated. Do not use controls as resource samples.

Ni/Co/Fe are elemental percent; MgO/SiO2/Al2O3/Cr2O3 are oxide percent.
SG in the full v4-derived data is modelled solid relative density, dimensionless;
it is not measured dry bulk density. Blank values remain missing, not zero.
Synthetic CC BY4.0: Ghozian Karami / Orebit.id. No field measurements or Mineral Resource statement.
PPT, notebooks, UI screenshots and the exact application/staging source are in the separate instructor package.
'''.encode()
files['LICENSE.txt'] = (BASE.parents[1] / 'LICENSE.txt').read_bytes()
# Preserve the reviewed QA/QC correction already published on main.
# Blank controls lack laboratory DL/LOR and must remain Not assessed.
files['dataset/exercises/qaqc-synthetic/README.txt'] = b'LATIHAN TAMBAHAN \xe2\x80\x94 QA/QC Ni SINTETIS\n\nGunakan project Assay terpisah. Upload qaqc-ni.csv, buka Data \xe2\x86\x92 QA/QC, lalu\npilih Ni (%). File ini berisi 11 baris: 3 kontrol SIMNI, 2 blank, 3 pasangan\nduplikat, dan 3 sampel pembanding biasa.\n\nSIMNI bukan certified reference material komersial. Masukkan mean simulasi\n1,00% Ni dan SD 0,04 dari output/exercises/reference-results/qaqc-mock-certificate-and-expected.json.\nZ-score hasilnya 0, 2, 5; kontrol terakhir harus dilaporkan gagal pada batas\nsimulasi 3 SD. Nilai ini hanya latihan, bukan sertifikat laboratorium.\n\nBlank bernilai 0,01% dan 0,08% Ni. Dataset tidak menyertakan DL/LOR yang\ndilaporkan laboratorium, sehingga keduanya harus berstatus Not assessed. Nilai\nterendah dalam dataset bukan DL/LOR dan tidak boleh dipakai sebagai pengganti.\nUntuk menilai blank, peserta perlu memakai DL/LOR resmi yang sesuai metode,\nmatriks, dan batch laboratorium; bila tidak tersedia, catat keterbatasannya.\n\nHARD duplikat = |asli \xe2\x88\x92 duplikat| / (asli + duplikat) \xc3\x97 100. Hasil latihan:\nCTRL01 2,4390%, CTRL02 27,2727%, CTRL03 4,7619%; satu pasangan melewati ambang\nlatihan 20%. Ambang ini bukan batas penerimaan universal.\n\nLatihan ini membuktikan bagaimana aplikasi menampilkan kontrol, bukan kelulusan\nQA/QC laboratorium atau mutu deposit. Jangan kirim baris kontrol ke domain,\ncomposite, atau estimasi Resource. Semua nilai dan metadata sintetis, CC BY 4.0\nGhozian Karami/Orebit.id.\n'
files['output/exercises/exercise_reference.py'] = b'"""Independent numerical teaching references, synthetic data only.\n\nCC BY 4.0 \xe2\x80\x94 Ghozian Karami / Orebit.id. This does not import GeoSuite code.\nRun with Python 3.12, NumPy, SciPy, pandas and matplotlib from the workshop pins.\n"""\n\nfrom pathlib import Path\nimport json\nimport math\nimport numpy as np\nimport pandas as pd\nfrom scipy.integrate import quad\nimport matplotlib.pyplot as plt\n\n\ndef direction(azimuth, dip):\n    az = math.radians(azimuth)\n    dip = math.radians(dip)\n    return np.array(\n        [math.cos(dip) * math.sin(az), math.cos(dip) * math.cos(az), -math.sin(dip)]\n    )\n\n\ndef point_at_md(collar, stations, md):\n    """Integrate the rotating tangent numerically, independently of the UI solver."""\n    if md < 0 or md > float(stations.AT.max()):\n        raise ValueError("Measured depth outside measured station support")\n    point = np.array([collar.XCOLLAR, collar.YCOLLAR, collar.ZCOLLAR], float)\n    ordered = list(stations.sort_values("AT").itertuples())\n    for a, b in zip(ordered[:-1], ordered[1:]):\n        if md <= a.AT:\n            break\n        fraction = min(1, (md - a.AT) / (b.AT - a.AT))\n        u, v = (direction(a.AZ, a.DIP), direction(b.AZ, b.DIP))\n        angle = math.atan2(float(np.linalg.norm(np.cross(u, v))), float(np.dot(u, v)))\n        if math.pi - angle < 1e-06:\n            raise ValueError("Opposite directions need measurement review")\n        for axis in range(3):\n\n            def tangent(t):\n                if angle < 1e-12:\n                    return u[axis]\n                return (\n                    math.sin((1 - t) * angle) * u[axis] + math.sin(t * angle) * v[axis]\n                ) / math.sin(angle)\n\n            point[axis] += (b.AT - a.AT) * quad(\n                tangent, 0, fraction, epsabs=1e-12, epsrel=1e-12\n            )[0]\n        if fraction < 1:\n            break\n    return point\n\n\ndef survey_reference(folder):\n    folder = Path(folder)\n    collar = pd.read_csv(folder / "collar.csv")\n    surveys = pd.read_csv(folder / "survey.csv")\n    assay = pd.read_csv(folder / "assay.csv")\n    rows = []\n    for c in collar.itertuples():\n        s = surveys[surveys.BHID == c.BHID]\n        a = assay[assay.BHID == c.BHID]\n        depths = sorted(set(s.AT.tolist() + ((a.FROM + a.TO) / 2).tolist()))\n        for md in depths:\n            x, y, z = point_at_md(c, s, md)\n            rows.append(\n                {"BHID": c.BHID, "MD": md, "X": x, "Y": y, "Z": z, "TVD": c.ZCOLLAR - z}\n            )\n    result = pd.DataFrame(rows)\n    expected = (\n        Path(__file__).parent / "reference-results/survey-expected-coordinates.csv"\n    )\n    if expected.exists():\n        reference = pd.read_csv(expected)\n        assert result.BHID.tolist() == reference.BHID.tolist()\n        assert (\n            np.max(\n                np.abs(\n                    result[["X", "Y", "Z"]].to_numpy()\n                    - reference[["X", "Y", "Z"]].to_numpy()\n                )\n            )\n            < 1e-07\n        )\n    return result\n\n\ndef qaqc_reference(folder):\n    folder = Path(folder)\n    data = pd.read_csv(folder / "qaqc-ni.csv")\n    certificate = json.loads(\n        (\n            Path(__file__).parent\n            / "reference-results/qaqc-mock-certificate-and-expected.json"\n        ).read_text()\n    )\n    assert (\n        certificate["synthetic_only"] and certificate["mock_certificate_not_real_CRM"]\n    )\n    crm = data[data.hole_id.str.startswith("CRM-")].copy()\n    crm["z"] = (crm.ni_pct - certificate["mean"]) / certificate["sd"]\n    blanks = data[data.hole_id.str.startswith("BLANK-")].copy()\n    paired = []\n    for row in data[data.hole_id.str.endswith("-DUP")].itertuples():\n        original = float(\n            data[data.hole_id == row.hole_id.removesuffix("-DUP")].ni_pct.iloc[0]\n        )\n        paired.append(\n            {\n                "original": original,\n                "duplicate": row.ni_pct,\n                "HARD": abs(original - row.ni_pct) / (original + row.ni_pct) * 100,\n            }\n        )\n    return (crm, blanks, pd.DataFrame(paired))\n\n\ndef plot_survey(folder, output):\n    folder = Path(folder)\n    output = Path(output)\n    output.mkdir(exist_ok=True, parents=True)\n    collars = pd.read_csv(folder / "collar.csv")\n    surveys = pd.read_csv(folder / "survey.csv")\n    plt.rcParams.update({"font.size": 14})\n    fig, axes = plt.subplots(1, 2, figsize=(12, 5))\n    for c in collars.itertuples():\n        stations = surveys[surveys.BHID == c.BHID]\n        md = np.linspace(0, float(stations.AT.max()), 120)\n        points = np.array([point_at_md(c, stations, float(d)) for d in md])\n        axes[0].plot(points[:, 0] - c.XCOLLAR, points[:, 2], label=c.BHID)\n        axes[1].plot(md, md - (c.ZCOLLAR - points[:, 2]), label=c.BHID)\n    axes[0].set(\n        xlabel="Easting displacement (m)",\n        ylabel="Elevation / RL (m)",\n        title="Curved measured-survey scenario",\n    )\n    axes[1].set(\n        xlabel="Measured depth (m)",\n        ylabel="MD minus TVD (m)",\n        title="Measured length differs from vertical depth",\n    )\n    axes[0].legend(fontsize=10)\n    fig.tight_layout()\n    fig.savefig(output / "survey-curvature.png", dpi=160)\n    plt.close(fig)\n\n\ndef plot_qaqc(folder, output):\n    output = Path(output)\n    output.mkdir(exist_ok=True, parents=True)\n    crm, blanks, pairs = qaqc_reference(folder)\n    plt.rcParams.update({"font.size": 14})\n    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))\n    axes[0].plot(range(1, len(crm) + 1), crm.z, "o-")\n    for threshold in [-3, 3]:\n        axes[0].axhline(threshold, color="#dc2626", ls="--")\n    axes[0].set(\n        xlabel="SIMNI control sequence",\n        ylabel="Z score",\n        title="Mock CRM: last control fails",\n    )\n    axes[1].bar(blanks.hole_id, blanks.ni_pct, color="#0f766e")\n    axes[1].set(ylabel="Ni (%)", title="Blank values: DL/LOR unavailable")\n    axes[1].text(\n        0.5,\n        0.95,\n        "Not assessed",\n        transform=axes[1].transAxes,\n        ha="center",\n        va="top",\n        color="#9a3412",\n    )\n    axes[1].tick_params(axis="x", labelsize=10)\n    axes[2].bar(\n        ["CTRL01", "CTRL02", "CTRL03"],\n        pairs.HARD,\n        color=["#0f766e", "#dc2626", "#0f766e"],\n    )\n    axes[2].axhline(20, color="#dc2626", ls="--")\n    axes[2].set(ylabel="HARD (%)", title="Duplicate precision")\n    axes[2].tick_params(axis="x", labelsize=10)\n    fig.tight_layout()\n    fig.savefig(output / "qaqc-mock-results.png", dpi=160)\n    plt.close(fig)\n\n\nif __name__ == "__main__":\n    root = Path(__file__).parent\n    data_root = (\n        root\n        if (root / "deviated-survey").exists()\n        else root.parents[1] / "dataset/exercises"\n    )\n    out = root / "calculated-output"\n    out.mkdir(exist_ok=True)\n    survey_reference(data_root / "deviated-survey").to_csv(\n        out / "survey-reference.csv", index=False\n    )\n    plot_survey(data_root / "deviated-survey", out)\n    plot_qaqc(data_root / "qaqc-synthetic", out)\n    print(\n        "Independent synthetic survey and mock QAQC references calculated; not professional validation."\n    )\n'
files['output/exercises/reference-results/qaqc-mock-certificate-and-expected.json'] = b'{\n  "synthetic_only": true,\n  "mock_certificate_not_real_CRM": true,\n  "group": "SIMNI",\n  "unit": "Ni elemental mass percent",\n  "mean": 1.0,\n  "sd": 0.04,\n  "lab_reported_DL_or_LOR": null,\n  "blank_assessment": "not_assessed_without_lab_reported_DL_or_LOR",\n  "crm_z": [\n    0,\n    2,\n    5\n  ],\n  "crm_failure_indices": [\n    2\n  ],\n  "blank_values_ni_pct": [\n    0.01,\n    0.08\n  ],\n  "blank_flag_indices": [],\n  "hard_percent": [\n    2.439024390243905,\n    27.27272727272727,\n    4.761904761904765\n  ],\n  "hard_threshold_percent": 20,\n  "normal_count": 3,\n  "duplicate_count": 3,\n  "blank_count": 2,\n  "crm_count": 3,\n  "estimation_use": "never: standalone QAQC exercise, no spatial/resource handoff"\n}\n'
files['BUILD.json'] = (json.dumps({'version': 5, 'base_data_commit': 'c4c65e5',
    'scope': 'Unchanged v4 data plus discoverable source-repair and analytical geometry exercises.',
    'files': {name: hashlib.sha256(body).hexdigest() for name, body in sorted(files.items())}}, indent=2) + '\n').encode()
for name, body in files.items():
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
archive = BASE / 'GeoSuite_Workshop_Nickel_v5.zip'
with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as target:
    for name, body in sorted(files.items()):
        info = zipfile.ZipInfo('GeoSuite_Workshop_Nickel_v5/' + name, (2026, 10, 27, 0, 0, 0))
        info.external_attr = 0o100644 << 16
        info.compress_type = zipfile.ZIP_DEFLATED
        target.writestr(info, body)
with zipfile.ZipFile(archive) as target:
    assert target.testzip() is None
archive.with_suffix('.zip.sha256').write_text(hashlib.sha256(archive.read_bytes()).hexdigest() + '  ' + archive.name + '\n')
print('v5:', len(files), 'files;', archive.stat().st_size, 'bytes;', hashlib.sha256(archive.read_bytes()).hexdigest())
