"""Independent exported-data checks plus a removed-budget mutation."""
from pathlib import Path
import hashlib,io,json,subprocess,sys,tempfile,zipfile
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve();BASE=HERE.parents[1]/'workshops/2026-11-05'
with zipfile.ZipFile(BASE/'GeoSuite_Workshop_Nickel_v3.zip') as z:
 old=pd.read_csv(io.BytesIO(z.read('GeoSuite_Workshop_Nickel_v3/dataset/assay.csv')))
 for name in ['collar.csv','survey.csv','litho.csv']:
  assert (BASE/'v4/dataset'/name).read_bytes()==z.read('GeoSuite_Workshop_Nickel_v3/dataset/'+name)
a=pd.read_csv(BASE/'v4/dataset/assay.csv');b=pd.read_csv(BASE/'v4/output/genesis/component-budget.csv')
assert a[['BHID','FROM','TO','NI_PCT','CO_PCT']].equals(old[['BHID','FROM','TO','NI_PCT','CO_PCT']])
assert a.isna().equals(old.isna())
ox=['FeO','Fe2O3','MgO','SiO2','Al2O3','Cr2O3','H2O','NiO','CoO']
assert np.max(np.abs(b[[c+'_MODEL_PCT' for c in ox]].sum(axis=1)-100))<1e-9
# Derive total Fe from separately recorded ferric/ferrous oxide masses.
fe=b.FeO_MODEL_PCT*55.845/(55.845+15.999)+b.Fe2O3_MODEL_PCT*(2*55.845)/(2*55.845+3*15.999)
finite=a.FE_PCT.notna();assert np.max(np.abs(fe[finite]-a.FE_PCT[finite]))<=.00501
assert a.iloc[:,3:10].sum(axis=1,min_count=7).dropna().max()<100
assert a.SG.min()>2.4 and a.SG.max()<5.3
code=(HERE.parent/'build_workshop_nickel_v4.py').read_text()
assert 'host[:,None]' in code
with tempfile.TemporaryDirectory() as td:
 root=Path(td);(root/'_generator').mkdir();(root/'workshops/2026-11-05').mkdir(parents=True)
 (root/'workshops/2026-11-05/GeoSuite_Workshop_Nickel_v3.zip').write_bytes((BASE/'GeoSuite_Workshop_Nickel_v3.zip').read_bytes())
 # Without the trace-element host budget, component masses exceed 100%.
 mutant=root/'_generator/build_workshop_nickel_v4.py';mutant.write_text(code.replace('host[:,None]','1'))
 run=subprocess.run([sys.executable,str(mutant)],capture_output=True,text=True)
 assert run.returncode!=0 and 'AssertionError' in run.stderr,'Removed mass-budget guard must fail'
print('PASS: raw Ni/Co/missing/geometry preserved; exported chemistry closure and Fe verified; removed-budget mutation fails')
