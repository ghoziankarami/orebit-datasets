"""Generate a disclosed mineral-budget teaching revision; never repair observed assays.

Geometry, Ni/Co fields and missing mask are frozen from the immutable v3 example.
Other chemistry and solid-mixture SG are newly simulated, not lab measurements.
"""
from pathlib import Path
import hashlib,io,json,shutil,zipfile
import numpy as np
import pandas as pd

BASE=Path(__file__).resolve().parents[1]/'workshops/2026-11-05'
SOURCE=BASE/'GeoSuite_Workshop_Nickel_v3.zip'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='e0f3e5c0d47ba9c31d44dfddd46375592cc885cbcf372ac50ecf9aea90d60aff'
OUT=BASE/'v4';OUT.mkdir(exist_ok=True)
with zipfile.ZipFile(SOURCE) as z:
 for item in z.infolist():
  relative=Path(*Path(item.filename).parts[1:])
  assert not relative.is_absolute() and '..' not in relative.parts
  if relative.parts and not item.is_dir():
   target=OUT/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(item))
raw=pd.read_csv(OUT/'dataset/assay.csv');old=raw.copy();logs=pd.read_csv(OUT/'dataset/litho.csv')
# Component mass fractions follow ideal formula stoichiometry, not assay normalisation.
A={'H':1.008,'O':15.999,'Mg':24.305,'Si':28.085,'Fe':55.845,'Al':26.9815385,'Cr':51.9961,'Ni':58.6934,'Co':58.933194}
def mass(formula):return sum(A[e]*n for e,n in formula.items())
MW={'FeO':mass({'Fe':1,'O':1}),'Fe2O3':mass({'Fe':2,'O':3}),'MgO':mass({'Mg':1,'O':1}),'SiO2':mass({'Si':1,'O':2}),'Al2O3':mass({'Al':2,'O':3}),'Cr2O3':mass({'Cr':2,'O':3}),'H2O':mass({'H':2,'O':1}),'NiO':mass({'Ni':1,'O':1}),'CoO':mass({'Co':1,'O':1})}
# rho are nominal endmember assumptions, sourced in genesis-method.md.
PHASES={
 'goethite':({'Fe2O3':.5,'H2O':.5},4.28),
 'hematite':({'Fe2O3':1},5.26),
 'serpentine':({'MgO':3,'SiO2':2,'H2O':2},2.55),
 'forsterite':({'MgO':2,'SiO2':1},3.275),
 'enstatite':({'MgO':1,'SiO2':1},3.20),
 'quartz':({'SiO2':1},2.65),
 'gibbsite':({'Al2O3':.5,'H2O':1.5},2.40),
 'chromite':({'FeO':1,'Cr2O3':1},4.65),
 'magnetite':({'FeO':1,'Fe2O3':1},5.18),
 'spinel':({'MgO':1,'Al2O3':1},3.58),
}
components=list(MW)
phase_names=list(PHASES)
chem=np.zeros((len(PHASES),len(components)));rho=[]
for i,(formula,density) in enumerate(PHASES.values()):
 total=sum(MW[c]*n for c,n in formula.items())
 for c,n in formula.items():chem[i,components.index(c)]=MW[c]*n/total
 assert abs(chem[i].sum()-1)<1e-12
 rho.append(density)
ENDS={
 'OVB':({'goethite':.55,'hematite':.25,'gibbsite':.12,'quartz':.03,'serpentine':.02,'chromite':.03},)*2,
 'LIM':({'goethite':.70,'hematite':.05,'gibbsite':.10,'quartz':.08,'serpentine':.04,'chromite':.03},{'goethite':.52,'hematite':.02,'gibbsite':.06,'quartz':.12,'serpentine':.26,'chromite':.02}),
 'SAP':({'goethite':.28,'hematite':.015,'gibbsite':.025,'quartz':.19,'serpentine':.475,'chromite':.015},{'goethite':.075,'gibbsite':.015,'quartz':.13,'serpentine':.63,'chromite':.01,'forsterite':.14}),
 'BRK':({'serpentine':.575,'forsterite':.22,'enstatite':.11,'magnetite':.075,'chromite':.015,'spinel':.005},)*2,
}
for ends in ENDS.values():
 for end in ends:assert abs(sum(end.values())-1)<1e-12
horizon=np.full(len(raw),'',dtype=object);rel=np.zeros(len(raw))
for hole,ids in raw.groupby('BHID',sort=False).groups.items():
 md=(raw.loc[ids,'FROM']+raw.loc[ids,'TO'])/2
 for r in logs[logs.BHID==hole].itertuples():
  use=md.index[(md>=r.FROM)&(md<r.TO)];horizon[use]=r.LITH;rel[use]=(md.loc[use]-r.FROM)/(r.TO-r.FROM)
assert (horizon!='').all()
rng=np.random.default_rng(20261025);w=np.zeros((len(raw),len(PHASES)))
for i,(unit,t) in enumerate(zip(horizon,rel)):
 top,bottom=ENDS[unit]
 w[i]=[(1-t)*top.get(p,0)+t*bottom.get(p,0) for p in phase_names]
# Modest compositional variation; all components are coupled by a unit mass budget.
# Original Ni spatial variability is held as an educational comparison, not fitted to r.
w*=np.exp(rng.normal(0,.12,w.shape));w/=w.sum(axis=1,keepdims=True)
ni=raw.NI_PCT.fillna(0).to_numpy();co=raw.CO_PCT.fillna(0).to_numpy()
nio=ni*MW['NiO']/A['Ni'];coo=co*MW['CoO']/A['Co'];host=1-(nio+coo)/100
assert (host>0).all()
budget=(w@chem)*host[:,None]*100
budget[:,components.index('NiO')]=nio;budget[:,components.index('CoO')]=coo
# NiO/CoO are accounting equivalents for trace substitution/hosts, not claimed XRD phases.
assert np.max(np.abs(budget.sum(axis=1)-100))<1e-10
idx={c:i for i,c in enumerate(components)}
raw['FE_PCT']=(budget[:,idx['FeO']]*A['Fe']/MW['FeO']+budget[:,idx['Fe2O3']]*2*A['Fe']/MW['Fe2O3']).round(2)
for col,c in [('MGO_PCT','MgO'),('SIO2_PCT','SiO2'),('AL2O3_PCT','Al2O3'),('CR2O3_PCT','Cr2O3')]:raw[col]=budget[:,idx[c]].round(3)
# Modelled solid relative density; excludes pore volume/water and is not dry bulk density.
solid_volume=host*np.sum(w/np.array(rho),axis=1)+(nio/100)/6.67+(coo/100)/6.44
raw['SG']=(1/solid_volume).round(3)
missing=old.NI_PCT.isna();grade_cols=['NI_PCT','CO_PCT','FE_PCT','MGO_PCT','SIO2_PCT','AL2O3_PCT','CR2O3_PCT']
raw.loc[missing,grade_cols]=np.nan
assert raw[['BHID','FROM','TO','NI_PCT','CO_PCT']].equals(old[['BHID','FROM','TO','NI_PCT','CO_PCT']])
assert np.array_equal(raw[grade_cols].isna(),old[grade_cols].isna())
# Verify the actual reported mixed elemental/oxide fractions, not a double-counted Fe sum.
assert (raw[grade_cols].sum(axis=1,min_count=7).dropna()<100).all()
raw.to_csv(OUT/'dataset/assay.csv',index=False)
audit=raw[['BHID','FROM','TO']].copy();audit['LITH']=horizon
for c in components:audit[c+'_MODEL_PCT']=budget[:,idx[c]]
audit['MODEL_CLOSURE_PCT']=budget.sum(axis=1);audit['SG_MODEL']=1/solid_volume
for k,p in enumerate(phase_names):audit[p+'_HOST_MASS_FRACTION']=w[:,k]
audit['ASSAY_MISSING']=missing
(OUT/'output/genesis').mkdir(exist_ok=True)
audit.to_csv(OUT/'output/genesis/component-budget.csv',index=False)
review=raw.assign(LITH=horizon).groupby('LITH')[grade_cols+['SG']].mean()
assert review.loc['SAP','NI_PCT']>review.loc['LIM','NI_PCT']>review.loc['BRK','NI_PCT']
assert review.loc['LIM','CO_PCT']>review.loc['SAP','CO_PCT']>review.loc['BRK','CO_PCT']
assert review.loc['LIM','FE_PCT']>review.loc['SAP','FE_PCT']>review.loc['BRK','FE_PCT']
assert review.loc['BRK','MGO_PCT']>review.loc['SAP','MGO_PCT']>review.loc['LIM','MGO_PCT']
assert review.loc['SAP','SIO2_PCT']>review.loc['LIM','SIO2_PCT']
assert raw.SG.between(2.4,5.3).all()
review.to_csv(OUT/'output/genesis/horizon-means.csv')
# Keep teaching defects as a named exercise, not as unexplained main-data chemistry.
shutil.copy2(OUT/'output/chemistry-review-flags.csv',OUT/'output/genesis/v3-legacy-chemistry-flags.csv')
for name in ['chemistry-review-flags.csv','chemistry-review.md']:(OUT/'output'/name).unlink(missing_ok=True)
checks={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (OUT/'dataset').glob('*.csv')}
(OUT/'output/input-checksums.json').write_text(json.dumps(checks,indent=2)+'\n')
receipt={'version':'v4','seed':20261025,'rows':len(raw),'missing_per_grade':int(missing.sum()),'Ni_Co_geometry_unchanged':True,'newly_simulated':['FE_PCT','MGO_PCT','SIO2_PCT','AL2O3_PCT','CR2O3_PCT','SG'],'main_partial_sum_over100':0,'maximum_component_closure_error':float(np.max(np.abs(budget.sum(axis=1)-100))),'legacy_v3_unchanged_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'not_measured_mineralogy_or_bulk_density':True,'raw_sha256':checks}
(OUT/'output/genesis/verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(review.round(4).to_string());print('PASS:',receipt)
