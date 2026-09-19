"""Reproduce seven species-specific historical phenology baselines (HF003, CC0).
Requires numpy. No 2026 observations, climate predictors or nationwide validation.
"""
import csv,json,datetime,collections,math,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
CODES={'acersacr':'ACSA','acerrubr':'ACRU','betupapy':'BEPA','poputrem':'POTR','querrubr':'QURU','nysssylv':'NYSY','fagugran':'FAGR'}
SPECIES=json.loads((DATA/'species.json').read_text())
annual=list(csv.DictReader((DATA/'phenology/hf003-08-fall-mean-spp.csv').open()))
raw=list(csv.DictReader((DATA/'phenology/hf003-04-fall.csv').open()))
def number(x):
 try:
  f=float(x);return f if math.isfinite(f) else None
 except (TypeError,ValueError):return None
def offset(year,doy):return doy-datetime.date(year,9,1).timetuple().tm_yday
def rounded(x):return round(float(x),2)
def crossing(seq,threshold):
 """First bracketed crossing, linear interpolation, maximum observation gap 21d.
 Apply cumulative max for non-monotonic field assessments; never extrapolate.
 """
 seq=sorted(seq);last=-1;mono=[]
 for d,v in seq:
  last=max(last,v);mono.append((d,last))
 for (d0,v0),(d1,v1) in zip(mono,mono[1:]):
  if v0<=threshold<=v1 and v1>v0 and 0<d1-d0<=21:
   return d0+(threshold-v0)/(v1-v0)*(d1-d0)
 return None
out={ 'version':1,'created':'2026-09-18','source':{'name':'Harvard Forest HF003 v37','doi':'https://doi.org/10.6073/pasta/bc5d2c15df4fa81aeadcd59ed7580c91','citation':"O’Keefe J, VanScoy G. 2024. Phenology of Woody Species at Harvard Forest since 1990. Harvard Forest Data Archive HF003 (v.37). Environmental Data Initiative.",'license':'CC0-1.0','lat':42.535,'lon':-72.185,'elevation':350,'spatialSites':1},'method':'Median annual published 50% dates; logistic curve widths from within-tree bracketed 10–90% transitions. Hold out latest 7 years (3 if <20 years), evaluate training-only constant median; then refit descriptive baseline on all years. Latitude/elevation transfer is NOT fitted or validated.','files':{},'species':{}}
for name in ['hf003-08-fall-mean-spp.csv','hf003-04-fall.csv']:
 out['files'][name]={'sha256':hashlib.sha256((DATA/'phenology'/name).read_bytes()).hexdigest(),'source':'https://harvardforest.fas.harvard.edu/data/p00/hf003/'+name}
for s in SPECIES:
 code=CODES.get(s['id']);candidates=[r for r in annual if r['species']==code];series=[]
 for r in candidates:
  y=int(r['year']);lc=number(r['lc.doy']);lf=number(r['lf.doy'])
  if lc is None or lf is None:continue
  lc=offset(y,lc);lf=offset(y,lf)
  if not (-30<=lc<=122 and -30<=lf<=122):continue
  series.append({'year':y,'color50':lc,'fall50':lf})
 series.sort(key=lambda r:r['year'])
 if len(series)<8:
  out['species'][s['id']]={'status':'uncalibrated','reason':'No matching HF003 reference-site time series; original illustrative model retained.'};continue
 raw_sp=[r for r in raw if r['tree.id'].startswith(code+'-')];widths={};width_samples={}
 for col in ['lcolor','lfall']:
  groups=collections.defaultdict(list)
  for r in raw_sp:
   value=number(r[col])
   if value is None or not 0<=value<=100:continue
   dt=datetime.date.fromisoformat(r['date']);groups[(dt.year,r['tree.id'])].append(((dt-datetime.date(dt.year,9,1)).days,value))
  peryear=collections.defaultdict(list)
  for (y,tree),seq in groups.items():
   a=crossing(seq,10);b=crossing(seq,90)
   if a is not None and b is not None and 2<=b-a<=80:peryear[y].append(b-a)
  vals=[float(np.median(v)) for v in peryear.values()];widths[col]=rounded(np.median(vals)/ (2*math.log(9))) if vals else None; width_samples[col]=len(vals)
 if any(v is None for v in widths.values()):raise ValueError('Insufficient width observations: '+code)
 hold=7 if len(series)>=20 else 3;train=series[:-hold];test=series[-hold:];train_lc=float(np.median([r['color50'] for r in train]));train_lf=float(np.median([r['fall50'] for r in train]));errors=[abs(r['color50']-train_lc) for r in test];fall_errors=[abs(r['fall50']-train_lf) for r in test]
 result={'status':'reference_calibrated','sourceCode':code,'nYears':len(series),'nRawObservations':len(raw_sp),'nIndividuals':len({r['tree.id'] for r in raw_sp}),'yearRange':[series[0]['year'],series[-1]['year']],'reference':{'lat':42.535,'lon':-72.185,'elevation':350},'color50':rounded(np.median([r['color50'] for r in series])),'fall50':rounded(np.median([r['fall50'] for r in series])),'colorScale':widths['lcolor'],'fallScale':widths['lfall'],'transitionYears':width_samples,'colorHistorical80':[rounded(x) for x in np.quantile([r['color50'] for r in series],[.1,.9])],'fallHistorical80':[rounded(x) for x in np.quantile([r['fall50'] for r in series],[.1,.9])],'validation':{'method':'chronological holdout; median baseline; reference site only','trainYears':[r['year'] for r in train],'testYears':[r['year'] for r in test],'trainColor50':rounded(train_lc),'trainFall50':rounded(train_lf),'colorMAE':rounded(np.mean(errors)),'fallMAE':rounded(np.mean(fall_errors)),'colorBias':rounded(np.mean([train_lc-r['color50'] for r in test])),'testPredictions':[{'year':r['year'],'observedColor50':r['color50'],'predictedColor50':rounded(train_lc),'absoluteError':rounded(abs(r['color50']-train_lc))} for r in test]},'annual':series}
 out['species'][s['id']]=result
 print(s['name'],len(series),'years',len(raw_sp),'records','color50',result['color50'],'MAE',result['validation']['colorMAE'])
(DATA/'calibration.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':')))
print('Calibrated',sum(x['status']=='reference_calibrated' for x in out['species'].values()),'of',len(SPECIES))
