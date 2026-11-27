"""Check that the open-pit validator catches broken surface files."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    "block_model.csv",
    "surface_topo.csv",
    "surface_topo.dxf",
    "collar.csv",
    "survey.csv",
    "assay.csv",
    "litho.csv",
)


class OpenPitValidation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for folder in ("04-emas-open-pit", "05-nikel-laterit-open-pit"):
            for name in FILES:
                source = ROOT / folder / name
                dest = self.root / folder / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, dest)
        (self.root / "_generator").mkdir()
        for script in ("validate_openpit.py", "common.py"):
            shutil.copyfile(ROOT / "_generator" / script, self.root / "_generator" / script)

    def tearDown(self):
        self.tmp.cleanup()

    def run_validator(self):
        return subprocess.run(
            [sys.executable, str(self.root / "_generator/validate_openpit.py")],
            cwd=self.root, text=True, capture_output=True,
        )

    def test_duplicate_xy_is_rejected(self):
        path = self.root / "04-emas-open-pit/surface_topo.csv"
        rows = path.read_text().splitlines()
        rows[-1] = ",".join(rows[2].split(",")[:2] + rows[-1].split(",")[2:])
        path.write_text("\n".join(rows) + "\n")
        result = self.run_validator()
        self.assertIn("GAGAL titik topografi membentuk grid reguler lengkap", result.stdout)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_dxf_extra_vertex_is_rejected(self):
        path = self.root / "04-emas-open-pit/surface_topo.dxf"
        lines = path.read_text().splitlines()
        face = lines.index("3DFACE")
        xcode = lines.index(" 10", face)
        lines[xcode + 1] = str(float(lines[xcode + 1]) + 1.0)
        path.write_text("\n".join(lines) + "\n")
        result = self.run_validator()
        self.assertIn("GAGAL titik sudut DXF cocok persis", result.stdout)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_non_meter_dxf_units_are_rejected(self):
        path = self.root / "04-emas-open-pit/surface_topo.dxf"
        path.write_text(path.read_text().replace(" 70\n6\n", " 70\n0\n", 1))
        result = self.run_validator()
        self.assertIn("GAGAL DXF menyatakan unit meter", result.stdout)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_floating_collar_is_rejected(self):
        path = self.root / "04-emas-open-pit/collar.csv"
        lines = path.read_text().splitlines()
        parts = lines[1].split(",")
        parts[3] = f"{float(parts[3]) + 2.5:.2f}"
        lines[1] = ",".join(parts)
        path.write_text("\n".join(lines) + "\n")
        result = self.run_validator()
        self.assertIn("GAGAL ZCOLLAR cocok dengan elevasi surface_topo.csv", result.stdout)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_overlapping_assay_intervals_are_rejected(self):
        path = self.root / "05-nikel-laterit-open-pit/assay.csv"
        lines = path.read_text().splitlines()
        parts = lines[2].split(",")
        parts[1] = "0.5"
        lines[2] = ",".join(parts)
        path.write_text("\n".join(lines) + "\n")
        result = self.run_validator()
        self.assertIn("GAGAL tidak ada interval assay bertumpang tindih", result.stdout)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
