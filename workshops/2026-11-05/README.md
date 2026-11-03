# GeoSuite Nickel Workshop dataset, 5th revision

Participant archive: [`GeoSuite_Workshop_Nickel_v5.zip`](GeoSuite_Workshop_Nickel_v5.zip)
SHA-256: `a5b7b867f607f2c55c8f90f80b787e26ab5e4fe0bb9f407207c218f8fb25cd31`
License: CC BY 4.0; all training data are synthetic.

The four baseline collar, survey, assay and lithology CSV files are unchanged
from v4. The additional exercise archive provides validation-repair examples,
a curved-survey minimum-curvature exercise, a small Domain known-answer case,
and separate synthetic QA/QC controls.

The QA/QC instructions and independent reference were corrected: CRM results
produce the teaching z-scores 0, 2 and 5; blank values remain **Not assessed**
because this dataset has no laboratory-reported DL/LOR; and one duplicate pair
exceeds the exercise HARD threshold. The observed minimum assay value is not a
substitute DL/LOR. Do not include control rows in Resource estimation.

The public archive is pinned by commit in the participant QR. No field data,
laboratory certificate, geological sign-off, or Mineral Resource classification
is implied.

## Workshop notebook

[`GeoSuite_Workshop_Nickel.ipynb`](GeoSuite_Workshop_Nickel.ipynb) repeats the
GeoSuite Surface-pair and Loft workflow in Python and checks each result
against the application. Outputs are saved in the file, so it can be read
without running it.

[Open in Google Colab](https://colab.research.google.com/github/ghoziankarami/orebit-datasets/blob/main/workshops/2026-11-05/GeoSuite_Workshop_Nickel.ipynb)

To run it in Colab, choose **Runtime → Run all**. The first cell asks for the
participant package ZIP (`Paket_Peserta_Workshop_ATI.zip`) distributed to
workshop participants; the notebook extracts it and reads the CSV files and
reference outputs from it.
