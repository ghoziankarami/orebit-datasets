GEOSUITE WORKSHOP NICKEL v5 — START HERE

Use a NEW PROJECT for each scenario. Never upload output/ or mix scenarios.

1 VALIDATION AND REPAIR
  Upload the four CSVs in dataset/exercises/validation/input/.
  Six source defects are intentional: missing X, duplicate collar, invalid azimuth,
  invalid dip, overlapping assay and mistyped hole ID. Locate exact rows in Core.
  For the retained source values and corrected reimport use output/exercises/validation-answer/.
  A green result after excluding faulty holes is not a completed repair.

2 MINIMUM CURVATURE
  Upload the four CSVs in dataset/exercises/deviated-survey/.
  Three holes,12survey stations; independent64-position references remain in
  output/exercises/reference-results/. Read the scenario README before importing.

3 DOMAIN -> ASSAY -> RESOURCE
  Simple Surface/Loft exercise: dataset/exercises/domain-known-answer/.
  CRS EPSG32748;36collars,72survey,108assays. SAP thickness6m and closed volume60000m3.
  World section corners and limitations: output/exercises/domain-known-answer.json.
  Full nickel laterite exercise: the four CSVs directly in dataset/ (EPSG32751).
  These340collar/680survey/8751assay/1344lithology rows and all chemical values
  are byte-identical to v4. Read output/genesis/genesis-method.md and the data dictionary.
  Geological interpretation, boundary decisions, actual filled support and density
  require separate explicit reviews; a successful UI action is not a geological signoff.

4 QA/QC — SEPARATE CONTROL DATA
  dataset/exercises/qaqc-synthetic/qaqc-ni.csv is for the Assay QAQC tool.
  Certificates/expected failures are simulated. Do not use controls as resource samples.

Ni/Co/Fe are elemental percent; MgO/SiO2/Al2O3/Cr2O3 are oxide percent.
SG in the full v4-derived data is modelled solid relative density, dimensionless;
it is not measured dry bulk density. Blank values remain missing, not zero.
Synthetic CC BY4.0: Ghozian Karami / Orebit.id. No field measurements or Mineral Resource statement.
PPT, notebooks, UI screenshots and the exact application/staging source are in the separate instructor package.
