"""Check reproducible open-pit snapshot packaging and tamper rejection."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("package_snapshot", ROOT / "_generator/package_snapshot.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class OpenPitSnapshot(unittest.TestCase):
    def test_reproducible_openpit_archive_and_counts(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            archive = module.package_openpit(ROOT, output, "tested-openpit-rev")
            first = archive.read_bytes()
            self.assertEqual(first, module.package_openpit(ROOT, output, "tested-openpit-rev").read_bytes())
            with zipfile.ZipFile(archive) as zip_file:
                zip_file.extractall(output / "unpacked")
            manifest = module.verify_openpit(output / "unpacked")
            self.assertEqual(manifest["bundle"], "openpit")
            self.assertEqual(manifest["source_ref"], "tested-openpit-rev")
            self.assertEqual(manifest["files"]["04-emas-open-pit/block_model.csv"]["rows"], 116056)
            self.assertEqual(manifest["files"]["04-emas-open-pit/collar.csv"]["rows"], 104)
            self.assertEqual(manifest["files"]["05-nikel-laterit-open-pit/block_model.csv"]["rows"], 28855)
            self.assertEqual(manifest["files"]["05-nikel-laterit-open-pit/collar.csv"]["rows"], 155)
            self.assertEqual(len([name for name in manifest["files"] if name.endswith(".csv")]), 12)
            self.assertEqual(len([name for name in manifest["files"] if name.endswith(".dxf")]), 2)

    def test_tampered_openpit_file_and_missing_entry_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = module.package_openpit(ROOT, root, "test-openpit")
            with zipfile.ZipFile(archive) as zip_file:
                zip_file.extractall(root)
            path = root / "04-emas-open-pit/collar.csv"
            original = path.read_bytes()
            path.write_bytes(original.replace(b"GK-001", b"GK-999", 1))
            with self.assertRaisesRegex(ValueError, "Snapshot differs"):
                module.verify_openpit(root)
            path.write_bytes(original)
            manifest_path = root / "DATA-MANIFEST.json"
            manifest = json.loads(manifest_path.read_text())
            del manifest["files"]["05-nikel-laterit-open-pit/surface_topo.dxf"]
            manifest_path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "surface_topo.dxf"):
                module.verify_openpit(root)


if __name__ == "__main__":
    unittest.main()
