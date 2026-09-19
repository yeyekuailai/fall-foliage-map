"""Compact Natural Earth public-domain city labels and generalized urban areas."""
import json,pathlib
from shapely.geometry import shape,mapping,box
R=pathlib.Path(__file__).resolve().parents[1]
source=json.loads((R/'work/cities-source.geojson').read_text())
cities=[]
for f in source['features']:
 p=f['properties'];lon,lat=f['geometry']['coordinates']
 if p.get('adm0_a3')=='USA' and -126<lon<-66 and 24<lat<50:
  cities.append({'name':p['name'],'state':p['adm1name'],'lat':round(lat,4),'lon':round(lon,4),'population':p['pop_max'],'rank':p['scalerank']})
cities.sort(key=lambda p:-p['population'])
(R/'data/cities.json').write_text(json.dumps(cities,separators=(',',':')))
features=[];bounds=box(-126,24,-66,50)
for f in json.loads((R/'work/urban-source.geojson').read_text())['features']:
 g=shape(f['geometry'])
 if g.intersects(bounds):
  g=g.intersection(bounds).simplify(.004,preserve_topology=True)
  if g.area>.0005:features.append({'type':'Feature','properties':{},'geometry':mapping(g)})
(R/'data/urban.json').write_text(json.dumps({'type':'FeatureCollection','features':features},separators=(',',':')))
print(len(cities),'cities',len(features),'urban polygons')
