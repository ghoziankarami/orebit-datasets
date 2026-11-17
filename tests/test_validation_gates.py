"""Exercise the actual CLI validators with valid and deliberately invalid CSVs."""

import csv
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDERS = ["01-emas-epitermal", "02-nikel-laterit", "03-timah-placer"]


class ValidationGates(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for folder in FOLDERS:
            shutil.copytree(ROOT / folder, self.root / folder)
        shutil.copytree(ROOT / "_generator", self.root / "_generator")
        shutil.copyfile(ROOT / "README.md", self.root / "README.md")

    def tearDown(self):
        self.tmp.cleanup()

    def run_checker(self, script):
        return subprocess.run(
            [sys.executable, str(self.root / "_generator" / script)],
            cwd=self.root,
            text=True,
            capture_output=True,
        )

    def test_recorded_statistics_allow_roundoff_but_reject_drift(self):
        import json, math

        path = self.root / "02-nikel-laterit/STATISTICS.json"
        original = json.loads(path.read_text())
        record = dict(original)
        record["ni_mean"] = math.nextafter(record["ni_mean"], math.inf)
        path.write_text(json.dumps(record))
        self.assertEqual(self.run_checker("check_readme.py").returncode, 0)
        record["valid_ni"] += 1
        path.write_text(json.dumps(record))
        self.assertNotEqual(self.run_checker("check_readme.py").returncode, 0)
        record = dict(original)
        record["ni_mean"] += 0.001
        path.write_text(json.dumps(record))
        self.assertNotEqual(self.run_checker("check_readme.py").returncode, 0)

    def test_valid_committed_datasets_pass_both_checkers(self):
        for script in ["validate.py", "check_readme.py"]:
            with self.subTest(script=script):
                result = self.run_checker(script)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_negative_grade_fails_validation(self):
        path = self.root / "03-timah-placer" / "assay.csv"
        rows = list(csv.reader(io.StringIO(path.read_text())))
        rows[1][rows[0].index("SN_KGM3")] = "-1"
        with path.open("w", newline="") as file:
            csv.writer(file).writerows(rows)
        result = self.run_checker("validate.py")
        self.assertIn("GAGAL tidak ada kadar negatif", result.stdout)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_changed_reference_count_fails_readme_checker(self):
        path = self.root / "01-emas-epitermal" / "collar.csv"
        lines = path.read_text().splitlines()
        path.write_text("\n".join(lines + [lines[1]]) + "\n")
        result = self.run_checker("check_readme.py")
        self.assertIn("GAGAL collar", result.stdout)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def reject_edit(self, folder, table, edit, message):
        path = self.root / folder / (table + ".csv")
        original = path.read_text()
        rows = list(csv.reader(io.StringIO(original)))
        edit(rows)
        try:
            with path.open("w", newline="") as file:
                csv.writer(file).writerows(rows)
            result = self.run_checker("validate.py")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("GAGAL " + message, result.stdout)
        finally:
            path.write_text(original)

    def test_orphan_references_fail_each_related_table(self):
        for table in ("survey", "assay", "litho"):
            with self.subTest(table=table):
                self.reject_edit(
                    FOLDERS[0],
                    table,
                    lambda rows: rows[1].__setitem__(0, "UNKNOWN-HOLE"),
                    "semua BHID %s ada di collar" % table,
                )

    def test_duplicate_collar_and_survey_station_fail(self):
        for table, message in (
            ("collar", "BHID collar unik"),
            ("survey", "stasiun survey BHID/AT unik"),
        ):
            with self.subTest(table=table):
                self.reject_edit(
                    FOLDERS[0], table, lambda rows: rows.append(rows[1].copy()), message
                )

    def test_overlap_is_rejected_for_assay_and_lithology(self):
        for table in ("assay", "litho"):
            with self.subTest(table=table):

                def overlap(rows):
                    rows[2][rows[0].index("FROM")] = rows[1][rows[0].index("FROM")]

                self.reject_edit(
                    FOLDERS[0],
                    table,
                    overlap,
                    "tidak ada interval %s bertumpang tindih" % table,
                )

    def test_lithology_must_stay_within_collar_depth(self):
        self.reject_edit(
            FOLDERS[0],
            "litho",
            lambda rows: rows[-1].__setitem__(rows[0].index("TO"), "10000"),
            "litho tidak melewati TD collar",
        )
        self.reject_edit(
            FOLDERS[0],
            "litho",
            lambda rows: rows[1].__setitem__(rows[0].index("FROM"), "-1"),
            "tidak ada litho FROM negatif",
        )

    def test_nonfinite_or_missing_geometry_fails(self):
        for table, column, value in (
            ("collar", "XCOLLAR", ""),
            ("collar", "TD", "inf"),
            ("survey", "AT", "NaN"),
            ("assay", "FROM", "inf"),
            ("litho", "TO", ""),
        ):
            with self.subTest(table=table, column=column):
                self.reject_edit(
                    FOLDERS[0],
                    table,
                    lambda rows: rows[1].__setitem__(rows[0].index(column), value),
                    "%s geometri numerik finite" % table,
                )

    def test_secondary_grades_and_density_are_checked(self):
        for folder, column, value, message in (
            (FOLDERS[0], "AG_GPT", "-1", "AG_GPT tidak negatif"),
            (FOLDERS[1], "CO_PCT", "inf", "CO_PCT nilai terisi finite"),
            (FOLDERS[2], "BD_TM3", "-1", "BD_TM3 tidak negatif"),
        ):
            with self.subTest(folder=folder, column=column):
                self.reject_edit(
                    folder,
                    "assay",
                    lambda rows: rows[1].__setitem__(rows[0].index(column), value),
                    message,
                )

    def test_wrong_unit_column_name_fails_schema_contract(self):
        self.reject_edit(
            FOLDERS[0],
            "assay",
            lambda rows: rows[0].__setitem__(rows[0].index("AU_GPT"), "AU_PCT"),
            "assay kolom wajib tersedia",
        )


if __name__ == "__main__":
    unittest.main()
