# 05 — Synthetic Open-Pit Nickel Laterite Block Model

Fictional **Lamonto** deposit. This teaching model represents a laterite profile
over ultramafic basement in an open-pit footprint. It is synthetic; it is not
data from a real mine or exploration project.

## Geometry and coordinate reference

- **CRS:** WGS 84 / UTM zone 51S, EPSG:32751; coordinates are metres.
- **Vertical datum:** MSL; Z is elevation in metres, positive up.
- **Block size:** 25 × 25 × 2 m, with cell-centre coordinates.
- **Footprint:** 1,150 × 950 m.
- **Topography:** lateritic hills sampled on a 25 m grid.
- **Profile:** variable overburden, limonite, saprolite, and bedrock thickness.

## Files

`block_model.csv` starts with a metadata comment containing CRS and vertical
datum. The next line is the table header. It contains 28,855 blocks, including
1,780 cells above topography retained to exercise surface clipping workflows;
27,075 cells lie at or below the modelled surface.

| Column | Unit / values | Meaning |
|---|---|---|
| `X`, `Y`, `Z` | m | Block-centre coordinates; Z positive up |
| `DX`, `DY`, `DZ` | m | Block dimensions (25, 25, 2) |
| `DENSITY` | t/m³ | Synthetic specific gravity / bulk-density proxy |
| `DOMAIN` | `OVB`, `LIM`, `SAP`, `BRK` | Overburden, limonite, saprolite, bedrock |
| `CLASS` | `Measured`, `Indicated`, `Inferred` | Synthetic confidence class based on modelled drilling spacing and extent |
| `NI_PCT`, `CO_PCT`, `FE_PCT`, `MGO_PCT`, `SIO2_PCT` | % | Synthetic element grades |

`surface_topo.csv` is a regular grid of `X,Y,Z` points. Its comment records the
CRS and vertical datum. `surface_topo.dxf` is the same surface as ASCII DXF
R12 `3DFACE` triangles on layer `TOPOGRAPHY`; every grid cell is split into two
triangles. The DXF header also records drawing units as metres. The surface
extends beyond the block footprint for interpolation at its edges.

### Spatially coherent drillholes (plain CSV headers)

Four plain-header drillhole tables (`collar.csv`, `survey.csv`, `assay.csv`,
`litho.csv`, with **no** `#` comment lines) are co-located with the topography
and 3D block model for cross-app workflows across **GeoSuite**, **Orebit
Desktop**, and **PitOpt** (see [Use with Orebit Apps](../docs/USE_WITH_OREBIT_APPS.md)):

- **`collar.csv`** (155 vertical holes `LM-001`–`LM-155`, `4,313.0 m` total,
  `TD` `13.0–48.0 m`, median `28.0 m`): 50 m infill over the central enrichment
  zone plus 100 m regional grid, collared on `surface_topo` (`240.90–394.71 m RL`).
- **`survey.csv`** (310 stations): collar (`0.0 m`) and `TD` with `AZ = 0.0°`
  and `DIP = 90.0°` (positive downward).
- **`assay.csv`** (4,313 `1.0 m` intervals:
  `BHID,FROM,TO,NI_PCT,CO_PCT,FE_PCT,MGO_PCT,SIO2_PCT,SG`): saprolite (`SAP`,
  `n = 1,783`) averages `1.42% Ni` (median `1.32%`, max `3.63%`); limonite
  (`LIM`, `n = 1,175`) averages `1.06% Ni`, `0.121% Co`, `42.2% Fe`; overall
  `FE_PCT` vs `MGO_PCT` correlation `r = -0.895` (`SG` `1.25–2.80 t/m³`).
- **`litho.csv`** (611 intervals: `BHID,FROM,TO,LITH`): contiguous `0..TD`
  laterite profile horizons (`OVB`, `LIM`, `SAP`, `BRK`).

## Grade and domain notes

Nickel enrichment is concentrated in the saprolite, while iron is higher in
limonite and magnesium/silica are higher in saprolite and bedrock. These
relationships are imposed by the generator and are useful for testing domain
statistics, cutoff selection, and blending workflows. They are not independent
geological observations. Domain and resource-class labels are teaching fields,
not estimates or classifications under JORC or KCMI.

For a PitOpt example, choose economic and geotechnical assumptions explicitly,
then clip blocks against `surface_topo.dxf` (or use the CSV surface when DXF
import is unavailable). Recovery, costs, dilution, blending penalties, and
operational constraints are not encoded in the model.

## Regenerate

From the repository root, install `_generator/requirements.txt` and run:

```bash
python _generator/gen_nikel_openpit.py
python _generator/validate_openpit.py
```

Seed `20260830` makes the generated files reproducible.

## Limitations and licence

This is a deterministic synthetic model for education, demonstrations, and
software testing. Geological geometry, grades, density, topography, and
confidence labels are designed inputs, not measured or independently validated
facts. Do not use it to support public resource or reserve reporting.

Licensed CC BY 4.0. Credit **Orebit.id**.
