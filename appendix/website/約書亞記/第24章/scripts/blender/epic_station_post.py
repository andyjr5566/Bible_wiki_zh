"""九站線性圖層 → 與紅海相同的分色、深度霧與 chosen 0.45 繪畫層。"""
import argparse, json, math, os, sys, time
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,HERE)
import numpy as np
from PIL import Image
import epic_post as E
import epic_plates_post as P
import style_a as S
from epic_station_config import IDS, config

def process(scene, work, out):
    started=time.perf_counter()
    meta=json.load(open(os.path.join(work,'meta.json'),encoding='utf-8'))
    w,h=meta['res']; C=config(scene)
    os.makedirs(out,exist_ok=True)
    sky=P.load_rgba(os.path.join(work,'sky.f32'),w,h)
    # 精確套用每站鏡頭仰角，不沿用紅海固定地平線。
    yh=int(h/2+math.tan(math.radians(C['pitch']))/(36*h/w/C['lens']/2)*h/2)
    band=np.minimum(sky[max(0,yh-18):max(1,yh-5),:,:3],1.5).mean(axis=0)
    hz=E.box_blur(band[None,:,:],max(3,w//40))[0]
    if C['night']:
        # 夜空的銀河與星月只屬天空，不把發光物帶入地面霧色。
        sr=np.array([int(C['horizon'][i:i+2],16)/255 for i in (1,3,5)],np.float32)
        base=np.where(sr>.04045,((sr+.055)/1.055)**2.4,sr/12.92)*C['strength']
        hz=np.broadcast_to(base,(w,3)).copy()
    hz_img=np.broadcast_to(hz[None,:,:],(h,w,3)).astype(np.float32)
    if scene=='beyond-river':
        # 河霧在遠方直接趨近該像素的天空輻射，不用較高處取樣的暖色帶
        # 填到水面末端，避免留下另一條亮色接縫。
        hz_img=np.minimum(sky[:,:,:3],1.5).copy()
    comp=np.zeros((h,w,3),np.float32)
    layers={}
    for plate in ('sky','far','mid','near'):
        rgba=sky if plate=='sky' else P.load_rgba(os.path.join(work,plate+'.f32'),w,h)
        alpha=np.clip(rgba[:,:,3],0,1)
        if plate=='sky': alpha[:]=1.
        col=np.where(alpha[:,:,None]>1e-5,rgba[:,:,:3]/np.maximum(alpha[:,:,None],1e-5),0).astype(np.float32)
        if plate in ('far','mid'):
            dep=P.load_rgba(os.path.join(work,plate+'_depth.f32'),w,h)
            # 深度 pass 有自己的抗鋸齒覆蓋率，不可除 beauty alpha。
            val=dep[:,:,0]/np.maximum(dep[:,:,3],1e-5)
            depth=np.clip(200.*(1/np.maximum(val,1e-6)-1),0,2e6)
            if plate=='mid' and scene in ('east','esau-jacob','beyond-river','moab'):
                # 真實深度控制的分層重疊，終點前已全透明。不是在影像上擦直線。
                d0,d1=(250.,950.) if scene=='beyond-river' else ((100.,400.) if scene=='moab' else (1800.,5200.))
                t=np.clip((depth-d0)/(d1-d0),0,1)
                alpha*=1-t*t*(3-2*t)
            # 陸地的兩層在同一高度場重疊；兩側霧律必須相同，不能在圖層交界變亮。
            hd=C['haze_far'] if plate=='far' or not C['river'] else C['haze_mid']
            haze=(1-np.exp(-depth/hd))*C['haze_mix']
            # 谷地薄霧：以世界高度與深度限制，近處岩石保有細節。
            height=dep[:,:,1]/np.maximum(dep[:,:,3],1e-5)*3500.-500.
            if scene in ('moab','canaan','jordan','east'):
                mist=np.exp(-np.maximum(height-10,0)/65)*(1-np.exp(-depth/2500))*.19
                haze=1-(1-haze)*(1-mist)
            col=col*(1-haze[:,:,None])+hz_img*haze[:,:,None]
            if scene=='east':
                # 遠谷低處的淡藍霧帶，保留較近崖壁的午後陰影。
                valley=np.exp(-np.maximum(height-15,0)/120)*(1-np.exp(-depth/2200))*.82
                col=col*(1-valley[:,:,None])+np.array([.07,.26,.50],np.float32)*valley[:,:,None]
        if plate=='near': col*=C['near_gain']
        if plate=='sky' and not C['night']:
            col=E.bloom(np.minimum(col,12.),1.3,.28)
        if plate=='mid' and C['river'] and scene!='egypt':
            col=E.bloom(np.minimum(col,12.),1.,.22)
        if scene=='egypt' and plate=='sky':
            # 雲縫的冷光：方向與真實太陽一致，只有一束，邊緣受雲狀雜訊打散。
            yy,xx=np.mgrid[0:h,0:w].astype(np.float32); xx/=w; yy/=h
            center=.70-.20*yy
            beam=np.exp(-((xx-center)/(.012+.065*yy))**2)
            gate=np.clip((yy-.16)/.18,0,1)*np.clip((.60-yy)/.12,0,1)
            cloud=E.gblur(np.random.default_rng(80).normal(size=(h,w)).astype(np.float32),14*w/1280)
            cloud=np.clip(.7+cloud*4,.2,1)
            col+=beam[:,:,None]*gate[:,:,None]*cloud[:,:,None]*np.array([.18,.25,.38],np.float32)
        col=E.grade(col,shadows=(.88,1.,1.18),highs=(1.15,1.,.84),sat=.95,split=.5,
                    gamma=.84 if C['night'] and plate in ('mid','far') else 1.)
        ldr=E.tonemap_filmic(col*C['exposure']*(C['sky_exposure'] if plate=='sky' else 1.))
        filled=P.fill_transparent(ldr,alpha) if plate!='sky' else ldr
        ldr=E.paint_overlay(np.clip(filled,0,1),dict(S.PAINT[S.PAINT_CHOICE]))
        # 保留原始透明輪廓；RGB 延伸防止視差縮放出現黑邊。
        img=Image.fromarray((np.clip(np.dstack((ldr,alpha)),0,1)*255+.5).astype(np.uint8),'RGBA')
        img.save(os.path.join(out,plate+'.png'))
        # composite 從實際 PNG 像素合成，讓驗收與網站疊圖一致。
        arr=np.asarray(img).astype(np.float32)/255.
        comp=comp*(1-arr[:,:,3:])+arr[:,:,:3]*arr[:,:,3:]
        layers[plate]=dict(alpha_min=int(np.asarray(img)[:,:,3].min()),alpha_max=int(np.asarray(img)[:,:,3].max()))
    Image.fromarray((np.clip(comp,0,1)*255+.5).astype(np.uint8),'RGB').save(os.path.join(out,'composite.png'))
    meta.update(post_seconds=round(time.perf_counter()-started,3),post_config=C,layers=layers)
    with open(os.path.join(out,'render-info.json'),'w',encoding='utf-8') as f: json.dump(meta,f,indent=2)
    print('POST_COMPLETE',scene,meta['post_seconds'],flush=True)
    return meta

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('scene',choices=IDS); ap.add_argument('--work',required=True); ap.add_argument('--out',required=True)
    a=ap.parse_args(); process(a.scene,a.work,a.out)
