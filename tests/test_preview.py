"""Smoke test for the preview generator; skipped when matplotlib/plotly are not installed."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_generator"))

try:
    import make_preview as mp
    import plotly  # noqa: F401
except ImportError:
    mp = None


@unittest.skipIf(mp is None, "matplotlib/plotly not installed")
class PreviewSmoke(unittest.TestCase):
    def test_every_dataset_has_a_config_and_folder(self):
        for name in mp.DATASETS:
            self.assertTrue((ROOT / name / "collar.csv").is_file(), name)

    def test_open_pit_preview_and_3d(self):
        name = "05-nikel-laterit-open-pit"
        with tempfile.TemporaryDirectory() as tmp:
            png = mp.draw_preview(name, out_dir=tmp)
            self.assertGreater(png.stat().st_size, 20_000)
            html = mp.build_3d(name, out_dir=tmp)
            self.assertIn("scatter3d", html.read_text())
        fig = mp.figure_3d(name)
        self.assertEqual({t.name for t in fig.data} >= {"topography", "drillholes", "assay samples"}, True)


if __name__ == "__main__":
    unittest.main()
