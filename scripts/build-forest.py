"""Create a compact, common-scale display raster from public USFS FHTET models.
The output is a historical relative basal-area proxy, never a tree census.
"""
import json, pathlib, urllib.parse, concurrent.futures, hashlib, subprocess
import numpy as np
from PIL import Image
import rasterio
from scipy.ndimage import gaussian_filter

ROOT=pathlib.Path(__file__).resolve().parents[1]
WORK=ROOT/'work/forest'; WORK.mkdir(exist_ok=True)
URL='https://imagery.geoplatform.gov/iipp/rest/services/Vegetation/USFS_EDW_FHP_TreeSpeciesMetrics_BasalArea/ImageServer'
SPECIES={'acersacr':'sugar_maple','acerrubr':'red_maple','betupapy':'paper_birch','poputrem':'quaking_aspen','querrubr':'northern_red_oak','liqustyr':'sweetgum','nysssylv':'blackgum','lirituli':'yellow_poplar','fagugran':'American_beech','acermacr':'bigleaf_maple'}
def get(item):
    sid,var=item; dest=WORK/(sid+'.tif')
    params={'f':'image','bbox':'-126,24,-66,50','bboxSR':4326,'imageSR':4326,'size':'1200,520','format':'tiff','pixelType':'U16','noData':0,'interpolation':'RSP_BilinearInterpolation','renderingRule':json.dumps({'rasterFunction':'None'}),'mosaicRule':json.dumps({'mosaicMethod':'esriMosaicNorthwest','where':"variable = '%s' AND year = 2002 AND category = 1"%var,'mosaicOperation':'MT_MAX'})}
    if not dest.exists():
        subprocess.run(['curl','--fail','--silent','--show-error','--max-time','120',URL+'/exportImage?'+urllib.parse.urlencode(params),'-o',str(dest)],check=True)
    with rasterio.open(dest) as ds: arr=ds.read(1,masked=True).filled(0).astype(float)
    assert arr.shape==(520,1200), (sid,arr.shape)
    arr[(arr<0)|(arr>60000)]=0
    print(sid, float(arr.max()), int(np.count_nonzero(arr)),flush=True)
    return sid,arr
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex: results=dict(ex.map(get,SPECIES.items()))
stack=np.stack([results[s] for s in SPECIES],axis=-1)
# Smooth the sampled display grid gently, not species boundaries or observations.
stack=gaussian_filter(stack,sigma=(.65,.65,0))
scale=float(np.percentile(stack[stack>0],99.7))
# Common scale preserves between-species relative abundance; no per-species stretch.
values=np.round(np.clip(stack/scale,0,1)*255).astype('uint8')
# Lossless PNG is a transport for ten numeric channels, laid side by side.
transport=np.concatenate([values[:,:,i] for i in range(10)],axis=1)
Image.fromarray(transport).save(ROOT/'data/forest-abundance.png',optimize=True)
meta={'width':1200,'height':520,'west':-126,'north':50,'step':.05,'species':list(SPECIES),'variables':SPECIES,'source':URL,'sourceTitle':'USFS FHTET individual tree species modeled basal area','vintage':'circa 2002','sourcePixelMeters':30,'displayResolution':'0.05 degrees; approximately 4–6 km; bilinear samples, not area means','unit':'relative modeled basal area, common scale across all species; not tree counts','commonScale':scale,'quantization':'round(clamp(value/commonScale,0,1)*255); zero includes no-data','smoothingSigmaPixels':.65,'transport':'one grayscale PNG, species bands arranged horizontally; north-to-south rows','retrieved':'2026-09-18','sourceHashes':{s:hashlib.sha256((WORK/(s+'.tif')).read_bytes()).hexdigest() for s in SPECIES}}
(ROOT/'data/forest-meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
print('Saved', (ROOT/'data/forest-abundance.png').stat().st_size,'bytes',flush=True)
