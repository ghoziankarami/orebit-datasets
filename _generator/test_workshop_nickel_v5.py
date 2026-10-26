"""Verify the new teaching scopes without using an application calculation."""
import csv
import hashlib
import io
import json
from pathlib import Path
import zipfile

BASE = Path(__file__).resolve().parents[1] / 'workshops/2026-11-05'
OUT = BASE / 'v5'
manifest = json.loads((OUT / 'BUILD.json').read_text())
assert manifest['version'] == 5
for name, digest in manifest['files'].items():
    assert hashlib.sha256((OUT / name).read_bytes()).hexdigest() == digest, name
for name in ['collar', 'survey', 'assay', 'litho']:
    assert (OUT / f'dataset/{name}.csv').read_bytes() == (BASE / f'v4/dataset/{name}.csv').read_bytes()

key = json.loads((OUT / 'output/exercises/validation-answer/answer-key.json').read_text())
assert len(key['faults']) == 6
repaired = {}
for name in ['collar', 'survey', 'assay', 'litho']:
    with (OUT / f'dataset/exercises/validation/input/{name}.csv').open(newline='') as source:
        repaired[name + '.csv'] = list(csv.DictReader(source))
for fault in reversed(key['faults']):
    rows = repaired[fault['file']]
    index = fault['csv_row'] - 2
    if fault['action'] == 'delete':
        assert rows[index] == rows[0]
        rows.pop(index)
    else:
        assert rows[index][fault['column']] == fault['faulty']
        rows[index][fault['column']] = fault['corrected']
for name, rows in repaired.items():
    with (OUT / 'output/exercises/validation-answer' / name).open(newline='') as answer:
        assert rows == list(csv.DictReader(answer)), name

fixture = OUT / 'dataset/exercises/domain-known-answer'
read = lambda name: list(csv.DictReader(io.StringIO((fixture / (name + '.csv')).read_text())))
assert len(read('collar')) == 36 and len(read('survey')) == 72
assert len(read('assay')) == len(read('litho')) == 108
sap = [row for row in read('litho') if row['LITH'] == 'SAP']
assert len(sap) == 36 and all(float(r['TO']) - float(r['FROM']) == 6 for r in sap)
oracle = json.loads((OUT / 'output/exercises/domain-known-answer.json').read_text())
assert oracle['sap_solid_m3'] == 100 * 100 * 6 == 60000
assert all(float(row['DIP']) == 90 and float(row['AZ']) == 0 for row in read('survey'))
assert sum(1 + i/10 + j/50 for i in range(6) for j in range(6)) / 36 == 1.3
archive = BASE / 'GeoSuite_Workshop_Nickel_v5.zip'
with zipfile.ZipFile(archive) as source:
    assert source.testzip() is None
    assert len(source.namelist()) == len(manifest['files']) + 1
    for name in manifest['files']:
        assert source.read('GeoSuite_Workshop_Nickel_v5/' + name) == (OUT / name).read_bytes()
print('PASS: immutable v4 chemistry/geometry, six exact reversible faults, analytical60000m3 fixture and all ZIP hashes')
