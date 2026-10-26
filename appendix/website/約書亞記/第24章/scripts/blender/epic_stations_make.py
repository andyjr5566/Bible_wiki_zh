"""九站總覽與機械驗收；渲染入口為 epic_stations_make.ps1。"""
import argparse, json, pathlib, sys
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from epic_station_config import IDS
ROOT=HERE.parent.parent
LAYERS=ROOT/'lab'/'renders'/'layers'

def contact(preview=False):
    from PIL import Image,ImageDraw,ImageFont
    base=LAYERS/'_work'/'previews' if preview else LAYERS
    sheet=Image.new('RGB',(1920,1170),'#151b24')
    draw=ImageDraw.Draw(sheet)
    font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',23)
    for i,scene in enumerate(IDS):
        img=Image.open(base/scene/'composite.png').convert('RGB').resize((640,360),Image.Resampling.LANCZOS)
        x=(i%3)*640; y=(i//3)*390
        sheet.paste(img,(x,y+30)); draw.text((x+12,y+3),scene,font=font,fill='#f0dfbd')
    path=base/('contact-preview-9.png' if preview else 'contact-9.png'); sheet.save(path)
    print('CONTACT',str(path),flush=True)

def verify():
    import numpy as np
    from PIL import Image
    errors=[]; summaries=[]
    for scene in IDS:
        arrays={}
        for plate in ('sky','far','mid','near'):
            p=LAYERS/scene/(plate+'.png'); im=Image.open(p)
            if im.size!=(1920,1080) or im.mode!='RGBA': errors.append(f'{scene}/{plate}: size/mode')
            arrays[plate]=np.asarray(im)
            alpha=arrays[plate][:,:,3]
            if plate=='sky' and alpha.min()!=255: errors.append(f'{scene}: sky not opaque')
            if plate!='sky' and (alpha.min()!=0 or alpha.max()!=255): errors.append(f'{scene}/{plate}: alpha range')
        comp=Image.open(LAYERS/scene/'sky.png').convert('RGBA')
        for plate in ('far','mid','near'): comp=Image.alpha_composite(comp,Image.open(LAYERS/scene/(plate+'.png')))
        saved=np.asarray(Image.open(LAYERS/scene/'composite.png')).astype(int)
        if saved.shape!=(1080,1920,3): errors.append(f'{scene}: composite size/mode')
        delta=np.abs(np.asarray(comp)[:,:,:3].astype(int)-saved)
        if delta.max()>2: errors.append(f'{scene}: composite mismatch {delta.max()}')
        n=arrays['near'][:,:,3]
        if (n[-1,:]!=255).any(): errors.append(f'{scene}: foreground bottom alpha hole')
        meta=json.loads((LAYERS/scene/'render-info.json').read_text(encoding='utf-8-sig'))
        if meta['paint_choice']!='chosen' or meta['paint_amount']!=.45: errors.append(f'{scene}: paint config')
        preview=Image.open(LAYERS/'_work'/'previews'/scene/'composite.png')
        if preview.size!=(1280,720): errors.append(f'{scene}: preview size')
        # 主地面上緣：取每欄自底往上首個連續不透明的像素，個別石草不當成地面。
        cover=(n>250).mean(axis=1)
        full=np.flatnonzero(cover>.95)
        ground_top=int(full[0]) if len(full) else 1080
        if not .15<=(1080-ground_top)/1080<=.20: errors.append(f'{scene}: foreground ground outside 15-20%')
        summaries.append(dict(scene=scene,near_ground_top=ground_top,near_ground_fraction=round((1080-ground_top)/1080,3),composite_delta=int(delta.max()),
                              blender_seconds=meta['total_seconds'],post_seconds=meta['post_seconds'],
                              render_seconds=round(meta['total_seconds']+meta['post_seconds'],2)))
    report=dict(errors=errors,station_count=len(IDS),image_count=len(IDS)*5,stations=summaries)
    (LAYERS/'verification-9.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
    if errors: raise SystemExit(1)

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('mode',choices=('contact','verify')); ap.add_argument('--preview',action='store_true')
    a=ap.parse_args()
    if a.mode=='contact': contact(a.preview)
    elif a.mode=='verify': verify()
