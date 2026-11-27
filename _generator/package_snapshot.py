"""Create and verify versioned teaching-data ZIP snapshots (standard library only)."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DATASETS = {
    "01-emas-epitermal": {"seed": 20260829, "epsg": 32748, "grade_units": {"AU_GPT": "g/t", "AG_GPT": "g/t", "SG": "t/m3"}},
    "02-nikel-laterit": {"seed": 20260830, "epsg": 32751, "grade_units": {"NI_PCT": "%", "CO_PCT": "%", "FE_PCT": "%", "MGO_PCT": "%", "SIO2_PCT": "%", "AL2O3_PCT": "%", "CR2O3_PCT": "%", "SG": "t/m3"}},
    "03-timah-placer": {"seed": 20260831, "epsg": 32748, "grade_units": {"SN_KGM3": "kg/m3", "BD_TM3": "t/m3"}},
}
TABLES = ("collar", "survey", "assay", "litho")

OPENPIT_DATASETS = {
    "04-emas-open-pit": {
        "seed": 20261125,
        "drillhole_seed": 20261125 + 1001,
        "epsg": 32748,
        "vertical_datum": "MSL",
        "block_size": [15.0, 15.0, 10.0],
        "grade_units": {"AU_GPT": "g/t", "AG_GPT": "g/t", "DENSITY": "t/m3", "SG": "t/m3"},
    },
    "05-nikel-laterit-open-pit": {
        "seed": 20260830,
        "drillhole_seed": 20260830 + 1001,
        "epsg": 32751,
        "vertical_datum": "MSL",
        "block_size": [25.0, 25.0, 2.0],
        "grade_units": {
            "NI_PCT": "%", "CO_PCT": "%", "FE_PCT": "%", "MGO_PCT": "%",
            "SIO2_PCT": "%", "DENSITY": "t/m3", "SG": "t/m3",
        },
    },
}
OPENPIT_CSV_TABLES = ("collar", "survey", "assay", "litho", "block_model", "surface_topo")
OPENPIT_SURFACES = ("surface_topo.dxf",)


def _csv_header_and_rows(data):
    """Parse CSV bytes ignoring '#' metadata comment lines and return (header, row_count)."""
    lines = [line for line in data.decode("utf-8").splitlines() if not line.startswith("#")]
    rows = list(csv.reader(io.StringIO("\n".join(lines))))
    if not rows:
        return [], 0
    return rows[0], len(rows) - 1


def _build_manifest(files, source_ref, datasets, extra=None):
    citation = files["CITATION.cff"].decode()
    version = re.search(r"^version:\s*['\"]?([^'\"\s]+)", citation, re.M).group(1)
    records = {}
    for name, data in files.items():
        record = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        if name.endswith(".csv"):
            columns, row_count = _csv_header_and_rows(data)
            record.update({"columns": columns, "rows": row_count})
        records[name] = record
    manifest = {
        "schema_version": 1,
        "version": version,
        "source_ref": source_ref,
        "synthetic": True,
        "license": "CC-BY-4.0",
        "datasets": datasets,
        "coordinate_unit": "m",
        "depth_unit": "m",
        "dip_convention": "positive down; 90 = vertical",
        "missing_value": "blank; never replace with zero implicitly",
        "files": records,
    }
    if extra:
        manifest.update(extra)
    return manifest


def _verify_files(root, manifest):
    for name, record in manifest["files"].items():
        path = Path(name)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("Unsafe manifest path")
        target = root / path
        if not target.is_file():
            raise ValueError("Missing snapshot file: " + name)
        data = target.read_bytes()
        if len(data) != record["bytes"] or hashlib.sha256(data).hexdigest() != record["sha256"]:
            raise ValueError("Snapshot differs from manifest: " + name)
        if name.endswith(".csv"):
            columns, row_count = _csv_header_and_rows(data)
            if columns != record["columns"] or row_count != record["rows"]:
                raise ValueError("CSV schema/count differs: " + name)


def _write_archive(archive, files, checksum_path):
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zip_file:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            zip_file.writestr(info, data, compresslevel=9)
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    checksum_path.write_text(f"{checksum}  {archive.name}\n")
    return archive


def payload(root):
    paths = [f"{folder}/{table}.csv" for folder in DATASETS for table in TABLES]
    paths += [f"{folder}/README.md" for folder in DATASETS]
    paths += ["README.md", "LICENSE.txt", "CITATION.cff", "docs/USE_WITH_GEOSUITE.md"]
    paths += [p.relative_to(root).as_posix() for p in sorted((root / "_generator").glob("*.py"))]
    paths += ["_generator/requirements.txt"]
    return {name: (root / name).read_bytes() for name in sorted(paths)}


def make_manifest(files, source_ref):
    return _build_manifest(files, source_ref, DATASETS)


def verify(root):
    manifest = json.loads((root / "DATA-MANIFEST.json").read_text())
    if manifest.get("schema_version") != 1 or manifest.get("synthetic") is not True:
        raise ValueError("Unsupported snapshot manifest")
    expected_csv = {f"{folder}/{table}.csv" for folder in DATASETS for table in TABLES}
    if {name for name in manifest["files"] if name.endswith(".csv")} != expected_csv:
        raise ValueError("Snapshot must contain the twelve training CSVs")
    _verify_files(root, manifest)
    return manifest


def package(root, output, source_ref="local-unrecorded"):
    files = payload(root)
    manifest = make_manifest(files, source_ref)
    files["DATA-MANIFEST.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f"orebit-datasets-{manifest['version']}.zip"
    return _write_archive(archive, files, output / "SHA256SUMS.txt")


def openpit_payload(root):
    paths = [f"{folder}/{table}.csv" for folder in OPENPIT_DATASETS for table in OPENPIT_CSV_TABLES]
    paths += [f"{folder}/{surf}" for folder in OPENPIT_DATASETS for surf in OPENPIT_SURFACES]
    paths += [f"{folder}/README.md" for folder in OPENPIT_DATASETS]
    paths += [
        "README.md", "LICENSE.txt", "CITATION.cff",
        "docs/USE_WITH_GEOSUITE.md", "docs/USE_WITH_OREBIT_APPS.md",
    ]
    paths += [p.relative_to(root).as_posix() for p in sorted((root / "_generator").glob("*.py"))]
    paths += ["_generator/requirements.txt"]
    return {name: (root / name).read_bytes() for name in sorted(paths)}


def make_openpit_manifest(files, source_ref):
    return _build_manifest(files, source_ref, OPENPIT_DATASETS, extra={"bundle": "openpit"})


def verify_openpit(root):
    manifest = json.loads((root / "DATA-MANIFEST.json").read_text())
    if (
        manifest.get("schema_version") != 1
        or manifest.get("synthetic") is not True
        or manifest.get("bundle") != "openpit"
    ):
        raise ValueError("Unsupported open-pit snapshot manifest")
    expected_csv = {f"{folder}/{table}.csv" for folder in OPENPIT_DATASETS for table in OPENPIT_CSV_TABLES}
    expected_dxf = {f"{folder}/{surf}" for folder in OPENPIT_DATASETS for surf in OPENPIT_SURFACES}
    if {name for name in manifest["files"] if name.endswith(".csv")} != expected_csv:
        raise ValueError("Open-pit snapshot must contain all twelve open-pit CSVs")
    if {name for name in manifest["files"] if name.endswith(".dxf")} != expected_dxf:
        raise ValueError("Open-pit snapshot must contain both surface_topo.dxf files")
    _verify_files(root, manifest)
    return manifest


def package_openpit(root, output, source_ref="local-unrecorded"):
    files = openpit_payload(root)
    manifest = make_openpit_manifest(files, source_ref)
    files["DATA-MANIFEST.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f"orebit-openpit-datasets-{manifest['version']}.zip"
    return _write_archive(archive, files, output / "SHA256SUMS-openpit.txt")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts")
    parser.add_argument("--source-ref", default="local-unrecorded")
    parser.add_argument("--bundle", choices=("drillholes", "openpit"), default="drillholes")
    parser.add_argument("--verify", type=Path, help="Verify an extracted snapshot against its manifest")
    args = parser.parse_args()
    if args.verify:
        result = verify_openpit(args.verify) if args.bundle == "openpit" else verify(args.verify)
        print(f"PASS: snapshot {result['version']}, source {result['source_ref']}")
    else:
        archive = (
            package_openpit(ROOT, args.output, args.source_ref)
            if args.bundle == "openpit"
            else package(ROOT, args.output, args.source_ref)
        )
        print(archive)
