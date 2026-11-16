"""Independent properties of the teaching model and deliberately faulty exercises."""

import csv, hashlib, importlib.util, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "nickel_layout", ROOT / "_generator/nickel_layout.py"
)
layout = importlib.util.module_from_spec(spec)
spec.loader.exec_module(layout)


def rows(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


class NickelTeaching(unittest.TestCase):
    def test_field_collars_are_visibly_displaced_from_planned_grid(self):
        c = pd.read_csv(ROOT / "02-nikel-laterit/collar.csv")
        planned = np.asarray(layout.drill_nodes())
        actual = c[["XCOLLAR", "YCOLLAR"]].to_numpy() - [392000.0, 9558000.0]
        displacement = np.linalg.norm(actual - planned, axis=1)
        self.assertGreater(np.median(displacement), 10.0)
        self.assertLess(displacement.max(), 45.0)
        self.assertTrue(all(layout.inside_prospect(*p) for p in actual))
        distances = np.linalg.norm(actual[:, None] - actual[None, :], axis=2)
        np.fill_diagonal(distances, np.inf)
        self.assertGreater(distances.min(), 18.0)

    def test_irregular_strike_footprint_and_infill(self):
        nodes = layout.drill_nodes()
        self.assertEqual(len(nodes), 350)
        self.assertEqual(len(set(nodes)), 350)
        self.assertTrue(all(layout.inside_prospect(*p) for p in nodes))
        points = np.array(nodes)
        eig = np.linalg.eigvalsh(np.cov(points.T))
        self.assertGreater(np.sqrt(eig[-1] / eig[0]), 1.8)
        self.assertTrue(any(x % 100 == 0 or y % 100 == 0 for x, y in nodes))
        self.assertFalse(layout.inside_prospect(50, 1450))
        self.assertFalse(layout.inside_prospect(1850, 50))

    def test_horizons_grade_and_density_behave_as_laterite(self):
        p = ROOT / "02-nikel-laterit"
        a = pd.read_csv(p / "assay.csv")
        l = pd.read_csv(p / "litho.csv")
        m = a.merge(l, on="BHID")
        m = m[(m.FROM_x >= m.FROM_y) & (m.TO_x <= m.TO_y)]
        sap = m[m.LITH == "SAP"]
        lim = m[m.LITH == "LIM"]
        brk = m[m.LITH == "BRK"]
        self.assertGreater(sap.NI_PCT.mean(), lim.NI_PCT.mean())
        self.assertGreater(lim.NI_PCT.mean(), brk.NI_PCT.mean())
        self.assertGreater(lim.FE_PCT.mean(), sap.FE_PCT.mean())
        self.assertGreater(sap.MGO_PCT.mean(), lim.MGO_PCT.mean())
        self.assertGreater(lim.CO_PCT.mean(), sap.CO_PCT.mean())
        self.assertLess(a.FE_PCT.corr(a.MGO_PCT), -0.7)
        self.assertTrue(a.SG.between(1.15, 2.85).all())
        self.assertGreater(brk.SG.mean(), sap.SG.mean())
        self.assertGreater(a.NI_PCT.isna().sum(), 0)
        self.assertTrue(a.loc[a.NI_PCT.isna(), "SG"].notna().all())

    def test_two_training_failures_are_specific_and_main_data_is_valid(self):
        main = ROOT / "02-nikel-laterit"
        c = rows(main / "collar.csv")
        s = rows(main / "survey.csv")
        holes = {r["BHID"] for r in c}
        self.assertEqual(holes, {r["BHID"] for r in s})
        bad = rows(ROOT / "exercises/missing-survey/survey.csv")
        self.assertEqual(len(holes - {r["BHID"] for r in bad}), 1)
        a = rows(main / "assay.csv")
        bad = rows(ROOT / "exercises/overlapping-assay/assay.csv")
        self.assertEqual(len(bad), len(a) + 1)
        self.assertEqual(bad[0]["BHID"], bad[1]["BHID"])
        self.assertLess(float(bad[1]["FROM"]), float(bad[0]["TO"]))
        for exercise in ("missing-survey", "overlapping-assay"):
            for table in ("collar", "litho"):
                self.assertEqual(
                    (main / f"{table}.csv").read_bytes(),
                    (ROOT / f"exercises/{exercise}/{table}.csv").read_bytes(),
                )

    def test_linkage_exercise_exposes_orphans_and_missing_geology(self):
        p = ROOT / "exercises/missing-collar-and-geology"
        c, s, a, g = (rows(p / (name + ".csv")) for name in ("collar", "survey", "assay", "litho"))
        holes = {r["BHID"] for r in c}
        self.assertEqual(len({r["BHID"] for r in a} - holes), 1)
        self.assertEqual(len({r["BHID"] for r in s} - holes), 1)
        self.assertEqual(len(holes - {r["BHID"] for r in g}), 1)
        self.assertEqual(len({r["BHID"] for r in g} - holes), 2)
        self.assertEqual(len(c), 349)

    def test_regeneration_reproduces_committed_csvs(self):
        with tempfile.TemporaryDirectory() as temp:
            clone = Path(temp)
            shutil.copytree(ROOT / "_generator", clone / "_generator")
            subprocess.run(
                [sys.executable, str(clone / "_generator/gen_nikel.py")],
                cwd=clone,
                check=True,
                capture_output=True,
            )
            for table in ("collar", "survey", "assay", "litho"):
                self.assertEqual(
                    (ROOT / f"02-nikel-laterit/{table}.csv").read_bytes(),
                    (clone / f"02-nikel-laterit/{table}.csv").read_bytes(),
                )


if __name__ == "__main__":
    unittest.main()
