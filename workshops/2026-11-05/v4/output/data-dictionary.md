# Data dictionary

Blank means missing, not zero. Headers map through native importer; never infer units from numerical magnitude.

|File|Column|Meaning/unit|
|---|---|---|
|collar.csv|BHID|Identifier; exact join key|
|collar.csv|XCOLLAR|Easting m|
|collar.csv|YCOLLAR|Northing m|
|collar.csv|ZCOLLAR|Collar RL m, positive up|
|collar.csv|TD|Measured total depth m; missing retained|
|survey.csv|BHID|Identifier; exact join key|
|survey.csv|AT|Survey station depth m|
|survey.csv|AZ|Azimuth degrees clockwise from North|
|survey.csv|DIP|Dip degrees positive downward;90vertical|
|assay.csv|BHID|Identifier; exact join key|
|assay.csv|FROM|Interval start m|
|assay.csv|TO|Interval end m|
|assay.csv|NI_PCT|Nickel grade percent|
|assay.csv|CO_PCT|Cobalt grade percent|
|assay.csv|FE_PCT|Iron grade percent|
|assay.csv|MGO_PCT|Magnesium oxide percent|
|assay.csv|SIO2_PCT|Silica percent|
|assay.csv|AL2O3_PCT|Alumina percent|
|assay.csv|CR2O3_PCT|Chromium oxide percent|
|assay.csv|SG|Modelled solid-mixture relative density (dimensionless); not measured and not dry bulk density|
|litho.csv|BHID|Identifier; exact join key|
|litho.csv|FROM|Interval start m|
|litho.csv|TO|Interval end m|
|litho.csv|LITH|Logged lithology, e.g.LIM/SAP|
