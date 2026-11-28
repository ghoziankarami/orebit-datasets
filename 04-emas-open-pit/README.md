# 04 — Synthetic Open-Pit Gold Block Model

Fictional **Gunung Kencana** deposit. This teaching model represents a
weathered, steeply dipping gold-silver stockwork system mined by an open pit.
It is synthetic; it is not data from a real mine or exploration project.

## Geometry and coordinate reference

- **CRS:** WGS 84 / UTM zone 48S, EPSG:32748; coordinates are metres.
- **Vertical datum:** MSL; Z is elevation in metres, positive up.
- **Block size:** 15 × 15 × 10 m, with cell-centre coordinates.
- **Model area:** 1,050 × 1,050 m; nominal vertical range 175–445 m RL.
- **Topography:** volcanic ridge and valley, sampled on a 20 m grid.
- **Mineralisation:** steep stockwork/vein envelope with two grade shoots;
  weathering domains follow variable depth below topography.

## Files

`block_model.csv` starts with a metadata comment containing CRS and vertical
datum. The next line is the table header. It contains 116,056 blocks, including
9,720 above-topography cells retained to exercise surface clipping workflows.
The remaining 106,336 blocks lie at or below the modelled topographic surface.

| Column | Unit / values | Meaning |
|---|---|---|
| `X`, `Y`, `Z` | m | Block-centre coordinates; Z positive up |
| `DX`, `DY`, `DZ` | m | Block dimensions (15, 15, 10) |
| `DENSITY` | t/m³ | Synthetic bulk density |
| `DOMAIN` | `OXIDE`, `TRANS`, `FRESH` | Weathering domain |
| `CLASS` | `Measured`, `Indicated`, `Inferred` | Synthetic confidence class based on modelled spacing and extent |
| `AU_GPT` | g/t | Gold grade |
| `AG_GPT` | g/t | Silver grade |

`surface_topo.csv` is a regular grid of `X,Y,Z` points. Its comment records the
CRS and vertical datum. `surface_topo.dxf` is the same surface as ASCII DXF
R12 `3DFACE` triangles on layer `TOPOGRAPHY`; every grid cell is split into two
triangles. The DXF header also records drawing units as metres. Both surface
files cover beyond the block-model footprint to support surface interpolation.

### Spatially coherent drillholes (plain CSV headers)

Four plain-header drillhole tables (`collar.csv`, `survey.csv`, `assay.csv`,
`litho.csv`, with **no** `#` comment lines) are co-located with the topography
and 3D block model for cross-app workflows across **GeoSuite**, **Orebit
Desktop**, and **PitOpt** (see [Use with Orebit Apps](../docs/USE_WITH_OREBIT_APPS.md)):

- **`collar.csv`** (104 angled holes `GK-001`–`GK-104`, `19,160.8 m` total,
  `TD` `133.3–232.9 m`, median `183.8 m`): 50 m infill in the mineralised corridor
  plus 100 m flank holes, collared on `surface_topo` (`319.30–432.49 m RL`).
- **`survey.csv`** (794 stations): 30 m downhole stations plus collar/TD,
  azimuth ~240° (drilling WSW across the 70° ENE dipping system) and
  positive-down dip `51.8°–70.0°`.
- **`assay.csv`** (12,669 intervals: `BHID,FROM,TO,AU_GPT,AG_GPT,SG`): `1.0 m`
  samples inside the mineralised core/halo and `2.0 m` in barren host rock;
  mineralised intervals (`AU_GPT >= 0.5 g/t`, `n = 3,118`) have mean `1.80 g/t`,
  median `1.34 g/t`, max `14.52 g/t` (overall mean `0.494 g/t Au`, `3.84 g/t Ag`,
  `SG` `1.92–2.86 t/m³`).
- **`litho.csv`** (412 intervals: `BHID,FROM,TO,LITH,ALT`): contiguous `0..TD`
  weathering domains (`OXIDE`, `TRANS`, `FRESH`) and alteration (`SIL`, `ARG`,
  `PROP`).

## Grade and domain notes

The model assigns gold and silver grades to mineralised core, lower-grade halo,
and background waste. Gold in the core is capped at 15 g/t by construction.
Domain and resource-class labels are generator rules for teaching software
workflows; they are not estimates or classifications under JORC or KCMI.

For a PitOpt example, select a cutoff and economic assumptions explicitly,
then clip blocks against `surface_topo.dxf` (or use the CSV surface when DXF
import is unavailable). The synthetic grades do not encode recovery, mining
cost, processing cost, dilution, or operational constraints.

## Regenerate

From the repository root, install `_generator/requirements.txt` and run:

```bash
python _generator/gen_emas_openpit.py
python _generator/validate_openpit.py
```

Seed `20261125` makes the generated files reproducible.

## Limitations and licence

This is a deterministic synthetic model for education, demonstrations, and
software testing. Geological geometry, grades, density, topography, and
confidence labels are designed inputs, not measured or independently validated
facts. Do not use it to support public resource or reserve reporting.

Licensed CC BY 4.0. Credit **Orebit.id**.
