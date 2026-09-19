/* Seven species have HF003 single-site historical baselines; spatial transfer remains
   an unvalidated assumption. Three species retain illustrative priors. See MODEL-NOTES.md. */
(function(root){
const clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));
let calibrated=true;
function calibration(s){return calibrated&&s.calibration?.status==='reference_calibrated'?s.calibration:null}
function transfer(s,lat,elevation=0){const c=calibration(s);return c?(c.reference.lat-lat)*s.latSlope-(elevation-c.reference.elevation)*s.elevationSlope:0}
function peak(s,lat,lon,elevation=0){const c=calibration(s);if(c)return c.color50+transfer(s,lat,elevation);const coastal=s.id==='acermacr'?Math.max(0,123+lon)*1.1:0;return clamp(s.peak+(42-lat)*s.latSlope-elevation*s.elevationSlope+coastal,5,112)}
const sigmoid=x=>1/(1+Math.exp(-clamp(x,-40,40)));
function fractions(s,day,lat,lon,elevation=0){const c=calibration(s);if(!c)return null;const t=transfer(s,lat,elevation);return {color:sigmoid((day-c.color50-t)/c.colorScale),fall:sigmoid((day-c.fall50-t)/c.fallScale)}}
function progress(s,day,lat,lon,elevation=0){const f=fractions(s,day,lat,lon,elevation);if(f)return clamp(.8*f.color+.2*f.fall);return clamp((day-peak(s,lat,lon,elevation))/s.duration+.64)}
function distanceToReference(s,lat,lon){const c=s.calibration;if(c?.status!=='reference_calibrated')return null;const rad=Math.PI/180,dlat=(lat-c.reference.lat)*rad,dlon=(lon-c.reference.lon)*rad;const a=Math.sin(dlat/2)**2+Math.cos(lat*rad)*Math.cos(c.reference.lat*rad)*Math.sin(dlon/2)**2;return 6371*2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a))}
function rgb(hex){return [1,3,5].map(i=>parseInt(hex.slice(i,i+2),16))}
function color(s,p){const x=clamp(p)*4,i=Math.min(3,Math.floor(x)),f=x-i,a=rgb(s.colors[i]),b=rgb(s.colors[i+1]);return a.map((v,k)=>Math.round(v+(b[k]-v)*f))}
function stage(p){return p<.18?'Green':p<.4?'Turning':p<.76?'Full color':p<.91?'Late autumn':'Leaf fall'}
function sample(bytes,meta,lon,lat,index){const x=(lon-meta.west)/meta.step,y=(lat-meta.south)/meta.step;if(x<0||y<0||x>=meta.width-1||y>=meta.height-1)return 0;const ix=Math.floor(x),iy=Math.floor(y),fx=x-ix,fy=y-iy;const at=(dx,dy)=>bytes[((iy+dy)*meta.width+ix+dx)*meta.channels+index]/255;return at(0,0)*(1-fx)*(1-fy)+at(1,0)*fx*(1-fy)+at(0,1)*(1-fx)*fy+at(1,1)*fx*fy}
root.AutumnModel={clamp,peak,progress,color,stage,sample,calibration,transfer,fractions,distanceToReference,setCalibrated:value=>{calibrated=!!value},isCalibrated:()=>calibrated};
})(typeof window==='undefined'?globalThis:window);
