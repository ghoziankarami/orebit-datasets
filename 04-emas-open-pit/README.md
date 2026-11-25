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
