# Dataset provenance

Orebit Synthetic Drillhole Datasets, CC BY4.0, credit Orebit.id. These are generated measurements, not field observations or a real nickel deposit.

Source: https://github.com/ghoziankarami/orebit-datasets/tree/6b93ac48df79264fda20e4ffc10716280bd2ee8a/02-nikel-laterit . Four CSVs derived by whole-hole selection:340holes,680survey stations,8751assay intervals,1344lithology intervals.10source holes lacking logged SAP base are excluded; no grade selection. Retained34Ni missing values are not zeros. Selection recipe/source hashes in raw/SELECTION.json. The generator source/reference pin and this subset are distinct from latest main README counts.

CRS WGS84/UTM51S (EPSG32751); projected XY/elevation/depth in meters; Z positive up, dip positive down. Ni/Fe/Co assay units as header declarations. Density1.6t/m³ in this exercise is an unverified uniform teaching assumption, not validated SG or deposit density. Contact interpolation maxedge200m and loft continuity are declared teaching interpretations. Pair:38collar locations sit on lateral mesh boundaries;468mofboundary support remains explicitly unassigned by the software policy.302interior holes contribute4122mofreviewed support. This is derived population selection, not loss of raw measurements. See boundary-support-audit.json.

Training baseline: surface SAP and separate LIM bodies; alternative3section loft has a different footprint. Their total tonnages are not an algorithm comparison on the same geology. All outputs are screening/training estimates, not classified or reportable Mineral Resources. No CP/fieldQAQC/RPE certification.
