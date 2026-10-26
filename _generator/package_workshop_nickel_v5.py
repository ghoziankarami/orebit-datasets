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

files['README.txt'] = '''GEOSUITE WORKSHOP NICKEL v5 — START HERE

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

4 QA/QC — SEPARATE CONTROL DATA
  dataset/exercises/qaqc-synthetic/qaqc-ni.csv is for the Assay QAQC tool.
  Certificates/expected failures are simulated. Do not use controls as resource samples.

Ni/Co/Fe are elemental percent; MgO/SiO2/Al2O3/Cr2O3 are oxide percent.
SG in the full v4-derived data is modelled solid relative density, dimensionless;
it is not measured dry bulk density. Blank values remain missing, not zero.
Synthetic CC BY4.0: Ghozian Karami / Orebit.id. No field measurements or Mineral Resource statement.
PPT, notebooks, UI screenshots and the exact application/staging source are in the separate instructor package.
'''.encode()
files['LICENSE.txt'] = (BASE.parents[1] / 'LICENSE.txt').read_bytes()
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
