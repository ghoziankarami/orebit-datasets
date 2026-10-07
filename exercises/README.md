# Core validation exercises

All three exercises use the same standard columns as the main nickel dataset. They are deliberately altered copies; these are not the default app sample.

- **missing-survey:** upload all four CSVs. One collar/assay hole has no survey records. Inspect linkage and geometry readiness; do not assume a vertical hole to hide the omission.
- **missing-collar-and-geology:** one collar is missing while its assays and survey remain; a second hole has no geology log; one geology identifier is inconsistent. Inspect orphan records and missing geology separately. Restore the original collar/logs; do not invent coordinates or silently merge identifiers.
- **overlapping-assay:** upload all four CSVs. One interval overlaps another interval in the first hole. Inspect interval validation; counting both would double-count sampled support.

Expected workflow: import → inspect validation → identify the affected hole/interval → explain the correction → replace the faulty table with its original from `02-nikel-laterit/` → revalidate before merging/exporting.

Use the main nickel table as the corrected answer. An aborted hole or a missing grade in the main dataset is a different case: the data can be valid but incomplete. Preserve blanks, document limitations, and do not invent grades or geometry.

Reproduce with `python _generator/make_core_exercises.py`. Exercises are synthetic, CC BY4.0, credit Orebit.id.
