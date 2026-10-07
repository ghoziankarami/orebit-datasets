# Lamonto — synthetic nickel laterite

A fictional tropical ultramafic prospect. The 350-hole programme follows a curved, strike-oriented footprint; its boundary is a sampling design, not an ore shell. All data are synthetic, CC BY 4.0, credit Orebit.id.

## Geological model

Ferricrete/overburden → limonite → saprolite → fresh peridotite. Laterite thickness follows slope: preserved on gentler crests and thinner on steeper slopes. Nickel peaks in upper saprolite, cobalt near the limonite/saprolite transition, while Fe decreases and MgO increases downward. The correlation lengths in the generator are model assumptions, not a fitted resource variogram.

| Horizon | Meaning | Mean logged thickness (m) | Valid Ni samples | Mean Ni (%) | Mean measured SG (t/m³) |
| --- | --- | ---: | ---: | ---: | ---: |
| OVB | Ferricrete / overburden | 1.29 | 424 | 0.707 | 1.531 |
| LIM | Limonite | 8.01 | 2,788 | 1.168 | 1.462 |
| SAP | Saprolite | 13.26 | 4,631 | 1.691 | 1.641 |
| BRK | Fresh bedrock penetrated by drilling | 2.77 | 1,019 | 0.289 | 2.620 |

## Drilling and files

**350 vertical holes, 8,811.5 m drilled.** Regional spacing is 100 m with selective 50 m infill following the prospect centre. Field collars depart from planned nodes by up to 44 m, preferring gentler local slopes with at least 20 m separation. This keeps a useful clustering exercise without a rectangular prospect outline.

- collar.csv: 350 rows; BHID, XCOLLAR, YCOLLAR, ZCOLLAR, TD. Fictional WGS84 / UTM 51S coordinates, metres.
- survey.csv: 700 rows; BHID, AT, AZ, DIP. Positive-down dip: 90° is vertical.
- assay.csv: 8,896 intervals, nominally 1 m; Ni, Co, Fe, MgO, SiO₂, Al₂O₃, Cr₂O₃ in percent and SG in t/m³.
- litho.csv: 1,372 intervals; BHID, FROM, TO, LITH.

10 holes stop in the weathered profile before fresh bedrock. 34 intervals have missing assays; measured SG is retained. Missing grades are blanks, not zeros.

## Sample statistics

These are unweighted sample statistics; they are not resource grades or contained metal. The active domain, composite support, density, search and geometry must be recorded separately when estimating.

Valid Ni n=8,862; mean **1.318%**, median 1.279%, maximum 3.657%, sample CV **0.456**. Fe–MgO correlation **-0.878**.

The full-precision sampled populations and counts are in STATISTICS.json. Opening all domains together mixes different weathering horizons; compare limonite and saprolite separately.

## Use in GeoSuite

1. Core: import all four tables; inspect linkage, missing assays, intervals and survey convention.
2. Assay: inspect distributions by horizon and record the composite length and any treatment.
3. Resource: choose the geological population and unit; inspect coverage, fit/test directional continuity, choose geometry and density, estimate, validate, then report a justified optional cutoff.

Carry measured SG through Core → Assay → Resource. A single assumed density needs its own justification; it should not silently replace measured values. The footprint is not a geological boundary, and the sample is not a certified resource.

## Core validation exercises

See ../exercises/README.md for missing-survey, overlapping-assay and missing-collar/geology cases. They are deliberately incomplete/invalid copies for teaching validation. Use the four tables in this directory for the main workflow.

## Reproduce

```bash
python _generator/gen_nikel.py
python _generator/nickel_summary.py
python _generator/make_core_exercises.py
python _generator/validate.py
python _generator/check_readme.py
```

Run from the repository root. Generator seed 20260830; layout uses nickel_layout.py. Reproducibility also requires the pinned NumPy/Pandas versions in _generator/requirements.txt.
