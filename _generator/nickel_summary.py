"""Document the synthetic nickel CSV revision using its actual sampled populations."""

import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def summary(root=ROOT):
    p = root / "02-nikel-laterit"
    c, s, a, l = (
        pd.read_csv(p / f"{n}.csv") for n in ("collar", "survey", "assay", "litho")
    )
    merged = a.merge(l, on="BHID")
    merged = merged[(merged.FROM_x >= merged.FROM_y) & (merged.TO_x <= merged.TO_y)]
    grades = a.NI_PCT.dropna()
    result = {
        "holes": len(c),
        "survey_rows": len(s),
        "assay_rows": len(a),
        "lithology_rows": len(l),
        "drilled_m": round(float(c.TD.sum()), 1),
        "valid_ni": len(grades),
        "missing_ni": int(a.NI_PCT.isna().sum()),
        "aborted_holes": len(c) - l[l.LITH == "BRK"].BHID.nunique(),
        "ni_mean": float(grades.mean()),
        "ni_median": float(grades.median()),
        "ni_max": float(grades.max()),
        "ni_cv": float(grades.std() / grades.mean()),
        "fe_mgo_r": float(a.FE_PCT.corr(a.MGO_PCT)),
        "horizons": {},
    }
    for horizon in ("OVB", "LIM", "SAP", "BRK"):
        pop = merged[merged.LITH == horizon]
        result["horizons"][horizon] = {
            "rows": len(pop),
            "valid_ni": int(pop.NI_PCT.notna().sum()),
            "ni_mean": float(pop.NI_PCT.mean()),
            "ni_cv": float(pop.NI_PCT.std() / pop.NI_PCT.mean()),
            "density_mean": float(pop.SG.mean()),
            "thickness_mean": float(l[l.LITH == horizon].eval("TO-FROM").mean()),
        }
    return result


def readme(d):
    lines = [
        "# Lamonto — synthetic nickel laterite",
        "",
        "A fictional tropical ultramafic prospect. The 350-hole programme follows a curved, strike-oriented footprint; its boundary is a sampling design, not an ore shell. All data are synthetic, CC BY 4.0, credit Orebit.id.",
        "",
        "## Geological model",
        "",
        "Ferricrete/overburden → limonite → saprolite → fresh peridotite. Laterite thickness follows slope: preserved on gentler crests and thinner on steeper slopes. Nickel peaks in upper saprolite, cobalt near the limonite/saprolite transition, while Fe decreases and MgO increases downward. The correlation lengths in the generator are model assumptions, not a fitted resource variogram.",
        "",
        "| Horizon | Meaning | Mean logged thickness (m) | Valid Ni samples | Mean Ni (%) | Mean measured SG (t/m³) |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    names = {
        "OVB": "Ferricrete / overburden",
        "LIM": "Limonite",
        "SAP": "Saprolite",
        "BRK": "Fresh bedrock penetrated by drilling",
    }
    for h in names:
        q = d["horizons"][h]
        lines.append(
            f"| {h} | {names[h]} | {q['thickness_mean']:.2f} | {q['valid_ni']:,} | {q['ni_mean']:.3f} | {q['density_mean']:.3f} |"
        )
    lines += [
        "",
        "## Drilling and files",
        "",
        f"**{d['holes']} vertical holes, {d['drilled_m']:,.1f} m drilled.** Regional spacing is 100 m with selective 50 m infill following the prospect centre. Field collars depart from planned nodes by up to 44 m, preferring gentler local slopes with at least 20 m separation. This keeps a useful clustering exercise without a rectangular prospect outline.",
        "",
        f"- collar.csv: {d['holes']} rows; BHID, XCOLLAR, YCOLLAR, ZCOLLAR, TD. Fictional WGS84 / UTM 51S coordinates, metres.",
        f"- survey.csv: {d['survey_rows']} rows; BHID, AT, AZ, DIP. Positive-down dip: 90° is vertical.",
        f"- assay.csv: {d['assay_rows']:,} intervals, nominally 1 m; Ni, Co, Fe, MgO, SiO₂, Al₂O₃, Cr₂O₃ in percent and SG in t/m³.",
        f"- litho.csv: {d['lithology_rows']:,} intervals; BHID, FROM, TO, LITH.",
        "",
        f"{d['aborted_holes']} holes stop in the weathered profile before fresh bedrock. {d['missing_ni']} intervals have missing assays; measured SG is retained. Missing grades are blanks, not zeros.",
        "",
        "## Sample statistics",
        "",
        "These are unweighted sample statistics; they are not resource grades or contained metal. The active domain, composite support, density, search and geometry must be recorded separately when estimating.",
        "",
        f"Valid Ni n={d['valid_ni']:,}; mean **{d['ni_mean']:.3f}%**, median {d['ni_median']:.3f}%, maximum {d['ni_max']:.3f}%, sample CV **{d['ni_cv']:.3f}**. Fe–MgO correlation **{d['fe_mgo_r']:.3f}**.",
        "",
        "The full-precision sampled populations and counts are in STATISTICS.json. Opening all domains together mixes different weathering horizons; compare limonite and saprolite separately.",
        "",
        "## Use in GeoSuite",
        "",
        "1. Core: import all four tables; inspect linkage, missing assays, intervals and survey convention.",
        "2. Assay: inspect distributions by horizon and record the composite length and any treatment.",
        "3. Resource: choose the geological population and unit; inspect coverage, fit/test directional continuity, choose geometry and density, estimate, validate, then report a justified optional cutoff.",
        "",
        "Carry measured SG through Core → Assay → Resource. A single assumed density needs its own justification; it should not silently replace measured values. The footprint is not a geological boundary, and the sample is not a certified resource.",
        "",
        "## Core validation exercises",
        "",
        "See ../exercises/README.md for missing-survey, overlapping-assay and missing-collar/geology cases. They are deliberately incomplete/invalid copies for teaching validation. Use the four tables in this directory for the main workflow.",
        "",
        "## Reproduce",
        "",
        "```bash",
        "python _generator/gen_nikel.py",
        "python _generator/nickel_summary.py",
        "python _generator/make_core_exercises.py",
        "python _generator/validate.py",
        "python _generator/check_readme.py",
        "```",
        "",
        "Run from the repository root. Generator seed 20260830; layout uses nickel_layout.py. Reproducibility also requires the pinned NumPy/Pandas versions in _generator/requirements.txt.",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    d = summary()
    p = ROOT / "02-nikel-laterit"
    (p / "STATISTICS.json").write_text(json.dumps(d, indent=2) + "\n")
    (p / "README.md").write_text(readme(d))
    print(json.dumps(d))
