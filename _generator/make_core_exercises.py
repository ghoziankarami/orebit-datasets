"""Deliberate validation failures; never replace the main training CSVs."""

import csv, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "02-nikel-laterit"
for name in ("missing-survey", "overlapping-assay"):
    dest = ROOT / "exercises" / name
    dest.mkdir(parents=True, exist_ok=True)
    for table in ("collar", "survey", "assay", "litho"):
        shutil.copyfile(source / f"{table}.csv", dest / f"{table}.csv")
    table = "survey" if name == "missing-survey" else "assay"
    with (dest / f"{table}.csv").open(newline="") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames
        rows = list(reader)
    hole = rows[0]["BHID"]
    if table == "survey":
        rows = [r for r in rows if r["BHID"] != hole]
    else:
        duplicate = dict(rows[0])
        duplicate["FROM"] = str((float(duplicate["FROM"]) + float(duplicate["TO"])) / 2)
        rows.insert(1, duplicate)
    with (dest / f"{table}.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, header, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
(ROOT / "exercises/README.md").write_text("""# Core validation exercises

Both exercises use the same standard columns as the main nickel dataset. They are deliberately altered copies; these are not the default app sample.

- **missing-survey:** upload all four CSVs. One collar/assay hole has no survey records. Inspect linkage and geometry readiness; do not assume a vertical hole to hide the omission.
- **overlapping-assay:** upload all four CSVs. One interval overlaps another interval in the first hole. Inspect interval validation; counting both would double-count sampled support.

Expected workflow: import → inspect validation → identify the affected hole/interval → explain the correction → replace the faulty table with its original from `02-nikel-laterit/` → revalidate before merging/exporting.

Use the main nickel table as the corrected answer. An aborted hole or a missing grade in the main dataset is a different case: the data can be valid but incomplete. Preserve blanks, document limitations, and do not invent grades or geometry.

Reproduce with `python _generator/make_core_exercises.py`. Exercises are synthetic, CC BY4.0, credit Orebit.id.
""")
print(
    "Prepared missing-survey and overlapping-assay exercises; primary CSVs unchanged."
)
