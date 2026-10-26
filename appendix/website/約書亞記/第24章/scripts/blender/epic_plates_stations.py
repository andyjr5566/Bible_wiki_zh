"""九站程序地形，EEVEE → 線性 RGBA + 深度。無人物、動物、建築。

blender -b --factory-startup --python scripts/blender/epic_plates_stations.py -- --scene isaac --w 1280 --h 720 --out lab/renders/layers/_work/preview/isaac
"""
import argparse, json, math, os, random, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import epic_lib as L  # 必須在 numpy 前載入應用程式控制繞法
import style_a as S
from epic_station_config import IDS, config
import bpy, bmesh
import numpy as np
from mathutils import Vector

ap = argparse.ArgumentParser()
ap.add_argument('--scene', choices=IDS, required=True)
ap.add_argument('--w', type=int, default=1280)
ap.add_argument('--h', type=int, default=720)
ap.add_argument('--samples', type=int, default=32)
ap.add_argument('--out', required=True)
ap.add_argument('--only', choices=('sky','far','mid','near'), nargs='+')
a = ap.parse_args(sys.argv[sys.argv.index('--')+1:])
C = config(a.scene)
rng = random.Random(C['seed'])
started = time.perf_counter()
os.makedirs(a.out, exist_ok=True)
previous={}
if a.only:
    with open(os.path.join(a.out,'meta.json'),encoding='utf-8') as f: previous=json.load(f)
    if previous['res']!=[a.w,a.h]: raise ValueError('Partial render resolution mismatch')
sc = L.fresh_scene('plates_'+a.scene)
world_cfg = {k:C[k] for k in ('sun_energy','sun_color','glow_k','glow','disc_k','disc_deg','horizon','mid','zenith','strength','clouds','cloud_scale','cloud_seed','fill','fill_color','cloud_lit')}
w, sun, sund = L.setup_world(C['sun_el'], C['az'],
                             ground=C['horizon'] if a.scene=='beyond-river' else C['below'], **world_cfg)
objs = {p:[] for p in ('sky','far','mid','near')}
def add(pl, ob):
    objs[pl].append(ob)
    return ob

def mat_ground(name, ca, cb, scale=.02, water=False, road=False, terraces=False):
    m = L.pbr(name, ca, .13 if water else .94)
    nt=m.node_tree; b=L.bsdf_of(m)
    tc=nt.nodes.new('ShaderNodeTexCoord')
    mp=nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value=(1., .12 if water else 1., 1.)
    nt.links.new(tc.outputs['Object'],mp.inputs['Vector'])
    n=L.noise_tex(nt,mp.outputs['Vector'],scale,5.,.65)
    n2=L.noise_tex(nt,tc.outputs['Object'],scale*11,3.,.58)
    fac=L.math_node(nt,'ADD',L.math_node(nt,'MULTIPLY',n,.75),L.math_node(nt,'MULTIPLY',n2,.25))
    col=L.mix_rgb(nt,L.srgb(ca),L.srgb(cb),fac)
    if road:
        attr=nt.nodes.new('ShaderNodeAttribute'); attr.attribute_name='road'
        col=L.mix_rgb(nt,col,L.srgb('#cfb58e'),L.math_node(nt,'MULTIPLY',attr.outputs['Fac'],.48))
    if terraces:
        attr=nt.nodes.new('ShaderNodeAttribute'); attr.attribute_name='terrace'
        col=L.mix_rgb(nt,col,L.srgb('#b6ab7a'),L.math_node(nt,'MULTIPLY',attr.outputs['Fac'],.35))
    if a.scene=='jordan' and name=='far_ground':
        sep=nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'],sep.inputs[0])
        oasis=L.math_node(nt,'MULTIPLY',L.math_node(nt,'SUBTRACT',1.,L.math_node(nt,'MINIMUM',L.math_node(nt,'DIVIDE',sep.outputs['X'],2000.),1.)),.75)
        col=L.mix_rgb(nt,col,L.srgb('#77895a'),oasis)
    if a.scene=='esau-jacob' and name=='mid_ground':
        geo=nt.nodes.new('ShaderNodeNewGeometry'); sep=nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(geo.outputs['Position'],sep.inputs[0])
        height=L.math_node(nt,'MINIMUM',L.math_node(nt,'MAXIMUM',L.math_node(nt,'DIVIDE',sep.outputs['Z'],130.),0.),1.)
        red=L.mix_rgb(nt,L.srgb('#8f4938'),L.srgb('#c6875a'),fac)
        col=L.mix_rgb(nt,col,red,height)
    nt.links.new(col,b.inputs['Base Color'])
    bump=nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value=.32 if water else .42
    bump.inputs['Distance'].default_value=.14 if water else .4
    if a.scene=='beyond-river' and water:
        bump.inputs['Strength'].default_value=.09
        bump.inputs['Distance'].default_value=.025
    nt.links.new(fac,bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],b.inputs['Normal'])
    if water:
        b.inputs['IOR'].default_value=1.33
        b.inputs['Specular IOR Level'].default_value=.7
        if a.scene=='egypt':
            b.inputs['Roughness'].default_value=.48
            b.inputs['Specular IOR Level'].default_value=.08
        if a.scene=='jordan':
            at=nt.nodes.new('ShaderNodeAttribute'); at.attribute_name='shoal'
            nt.links.new(L.mix_rgb(nt,col,L.srgb('#8f9c80'),at.outputs['Fac']),b.inputs['Base Color'])
    return m

def grid(x0, x1, nx=440, ny=510, power=2.5):
    xs=x0+(x1-x0)*np.linspace(0.,1.,nx)**power
    X=np.broadcast_to(xs[None,:],(ny,nx)).copy()
    Y=np.linspace(-1.,1.,ny)[:,None]*(np.maximum(X,0)+100.)*1.5
    return X,Y

def noise(X,Y,wl,minimum,seed=0):
    return L.fbm2(X,Y,wl,minimum,seed=C['seed']+seed)

def terrain(X,Y):
    """連續全幅高度場；far 與 mid 在同一函式上重疊，無直線斷層。"""
    n=noise(X,Y,950.,40.,1)
    big=noise(X,Y,5800.,320.,3)
    if a.scene=='isaac':
        z=.5+.8*n
        for k,(x,h,wl) in enumerate(((1800,35,1800),(5000,240,3300),(11000,760,4800),(23000,1900,9000))):
            axis=x+450*noise(Y,Y*0,wl,wl/8,8+k)
            profile=.72+.72*noise(Y,Y*0,wl*.65,wl/18,14+k)
            z+=h*np.exp(-((X-axis)/(x*.25+270))**2)*profile
        return z
    if a.scene=='wilderness':
        # 平原極空；遠方花崗岩由多尺度脊線與稜面構成。
        z=.15+.45*n
        for k,(x,h) in enumerate(((4200,400),(8500,700),(16000,950))):
            ridge=(1-np.abs(noise(X,Y,1800+800*k,80.,19+k)))**2.3
            axis=x+800*noise(Y,Y*0,2600,220,25+k)
            z+=h*np.exp(-((X-axis)/(1000+600*k))**2)*(.3+ridge)
        return z
    if a.scene=='esau-jacob':
        left=L.smoothstep(-.05,.45,Y/(np.maximum(X,0)+80))
        axis=4200+950*noise(Y,Y*0,5000,200,12)
        ridge=(1-np.abs(noise(X,Y,1600,70,17)))**3
        mountain=750*np.exp(-((X-axis)/1850)**2)*(.18+ridge)+220*np.exp(-((X-10500)/5000)**2)
        dunes=(7*np.sin(X/120+Y/230+2*noise(X,Y,800,70,76))
               +11*noise(X,Y,420,35,77)+26*noise(X,Y,1800,120,78))
        dunes*=L.smoothstep(60,350,X)*(1-.8*left)
        ripples=12*noise(X,Y,100,9,79)*L.smoothstep(80,250,X)
        ripples+=2.2*noise(X,Y,18,2,182)*L.smoothstep(40,120,X)
        return 1+2*n+12*big+dunes+ripples+left*mountain*L.smoothstep(600,2000,X)
    if a.scene=='east':
        # 侵蝕台地：封閉曲線控制輪廓，支溝侵入崖緣；不乘矩形側面遮罩。
        z=3+5*n+18*big
        for k,(cx,cy,rx,ry,h) in enumerate(((2100,1600,1450,2200,240),
                                          (6400,3700,2900,4500,580),
                                          (15900,4100,5900,12000,1500),
                                          (34000,0,10500,33000,2300))):
            u=(X-cx)/rx; v=(Y-cy)/ry
            r=(np.abs(u)**3+np.abs(v)**3)**(1/3)
            warp=.15*noise(X,Y,rx*.7,rx/24,22+k)
            gullies=(1-np.abs(noise(X*.22,Y,160+140*k,20+15*k,82+k)))**9
            rim=r+warp+.085*gullies+.035*noise(X,Y,150+180*k,18+15*k,102+k)
            mass=1-L.smoothstep(.86,1.06,rim)
            cap=1+.085*noise(X,Y,rx*.6,rx/28,92+k)+.055*noise(X,Y,120+120*k,15+12*k,112+k)
            z+=h*mass*cap
            z-=h*.13*gullies*np.exp(-((rim-.94)/.15)**2)
        return z
    if a.scene=='moab':
        z=(12+14*n+55*big+25*noise(X,Y,220,20,49)
           +20*noise(X,Y,95,10,175)+12*noise(X,Y,35,4,176))
        for k,(x,h,wl) in enumerate(((2200,100,2400),(6500,170,4200),(14000,360,8000),(35000,800,15000))):
            axis=x+650*noise(Y,Y*0,wl,wl/8,52+k)
            profile=1+.65*noise(X,Y,wl,wl/12,56+k)+.6*noise(X,Y,350+300*k,30+25*k,156+k)
            z+=h*np.exp(-((X-axis)/(1000+k*650))**2)*profile
        z+=120*L.smoothstep(11000,19000,X)*(1+.5*noise(X,Y,8000,500,31))
        # 低處寬闊的谷地與曲折乾河床。
        channel=moab_channel(X)
        slope=(moab_channel(X+1)-moab_channel(X-1))*.5
        dist=np.abs(Y-channel)/np.sqrt(1+slope*slope)
        valley=L.smoothstep(90,680,dist)
        z=z*valley+2*(1-valley)
        return z
    if a.scene=='canaan':
        z=8+8*n
        for k,(x,h,wl) in enumerate(((600,80,1600),(2300,300,2800),(5700,750,4200),(12000,1400,7000),(23000,2700,11000))):
            axis=x+(.27*x+100)*noise(Y,Y*0,wl,wl/8,9+k)
            profile=.8+1.05*noise(Y,Y*0,wl*.7,wl/16,17+k)
            crumple=1+.25*noise(X,Y,wl*.3,wl/30,25+k)
            z+=h*np.exp(-((X-axis)/(x*.22+250))**2)*profile*crumple
        # 梯田只在近中景的緩坡，以不連續田塊遮罩避免等高線覆滿山體。
        mask=L.smoothstep(-.15,.22,noise(X,Y,280,35,44))*(1-L.smoothstep(2500,3800,X))
        stepped=np.floor(z/6)*6+6*L.smoothstep(.0,.25,(z%6)/6)
        z=z*(1-mask*.8)+stepped*mask*.8
        return z
    if a.scene=='jordan':
        z=.8+.8*n
        for k,(x,h,wl) in enumerate(((2800,190,2000),(6500,530,4300),(14000,1200,7000))):
            axis=x+450*noise(Y,Y*0,wl,wl/9,61+k)
            profile=.7+.7*noise(Y,Y*0,wl*.7,wl/15,65+k)
            z+=h*np.exp(-((X-axis)/(650+k*700))**2)*profile*L.smoothstep(700,1800,X)
        return z
    if a.scene=='beyond-river':
        return .8+.5*n+L.smoothstep(9000,15000,X)*(12+24*(.5+.5*big))
    return .8+.5*n+L.smoothstep(14000,23000,X)*(10+12*big)

def moab_channel(X):
    # 下游彎曲也要在透視投影中可讀；近谷有兩次明顯轉彎。
    # 山頂俯瞰時，過寬的大 S 彎會被壓成長直段。較小的連續彎道隨
    # 距離逐漸展開，在這個鏡頭仍可看見多次轉向。
    return X*(.04+.095*np.sin(280000/(np.maximum(X,0)+400)/22+.8))

if not C['river']:
    # 丘陵的高斯尾部也有高度；先將鏡頭腳下歸零，避免低機位埋入地表。
    terrain_raw=terrain
    terrain_origin=float(terrain_raw(np.array([[0.]]),np.array([[0.]]))[0,0])
    def terrain(X,Y):
        return terrain_raw(X,Y)-terrain_origin

def shore(Y):
    return C['bank']+(.065*C['bank'])*noise(Y,Y*0,C['bank']*.8,20,42)

ground=mat_ground('mid_ground',C['ground'],C['far_b'],.11,road=a.scene=='esau-jacob',terraces=a.scene=='canaan')
far_mat=mat_ground('far_ground',C['far_a'],C['far_b'],.003) if C['river'] else ground
near_mat=mat_ground('near_earth',C['rock'],C['ground'],2.)
if C['river']:
    X,Y=grid(-80, 150000 if a.scene=='beyond-river' else max(C['bank']+250,1700),
             680 if a.scene=='beyond-river' else 390,530,3. if a.scene=='beyond-river' else 2.)
    Z=np.zeros_like(X)+.006*noise(X,Y,5,.6,52)
    attrs={}
    if a.scene=='jordan':
        center=11+12*np.sin(X/45)
        attrs['shoal']=.48*np.exp(-((Y-center)/9)**2)
        Z+=.035*np.sin(X*3+Y*.7)*np.exp(-((Y-center)/14)**2)
    water=mat_ground('river_water','#152d38' if a.scene!='egypt' else '#1e303b','#426775' if a.scene!='egypt' else '#40505a',.85,water=True)
    water_ob=add('mid',L.mesh_from_grid('river_surface',X,Y,Z,attrs,water))
    if a.scene=='beyond-river':
        # 水與岸同一遠景中做深度遮擋；中景水漸隱到同一完整水面。
        add('far',L.instance(water_ob.data,'river_under_bank',(0,0,0)))
    X,Y=grid(C['bank']-100,150000,490,560,3.)
    # 真正的河岸輪廓由頂點位置塑成，水面穿過平滑坡腳。
    X=X+shore(Y)-C['bank']
    Z=terrain(X,Y)*L.smoothstep(shore(Y)-80,shore(Y)+45,X)
    Z-=.18*(1-L.smoothstep(shore(Y)-60,shore(Y),X))
    bank_ob=add('far',L.mesh_from_grid('far_bank',X,Y,Z,None,far_mat))
elif a.scene=='moab':
    # 山頂岩台與谷地各自獨立；岩台前緣是下切的實體坡壁。
    X,Y=grid(-90,520,440,620,1.7)
    edge=19.+9*noise(Y,Y*0,65,4,70)+4*np.sin(Y/13)
    drop=L.smoothstep(edge-4,edge+52+12*noise(X,Y,35,4,72),X)
    plain=terrain(X,Y)
    rocktop=(C['camera']-3.8+1.8*noise(X,Y,18.,1.8,71)+.6*np.sin(Y/7+X/13)
             +.45*noise(Y,Y*0,4.,.4,74)+.18*np.sin(Y*2.3+1))
    Z=rocktop*(1-drop)+plain*drop
    add('mid',L.mesh_from_grid('summit_ledge',X,Y,Z,None,near_mat))
    X,Y=grid(-90,150000,1100,1100,3.2)
    t=np.linspace(-1,1,1100)[:,None]
    Y=moab_channel(X)+np.sign(t)*np.abs(t)**1.8*(np.maximum(X,0)+2000)*1.7
    slope=(moab_channel(X+1)-moab_channel(X-1))*.5
    dist=np.abs(Y-moab_channel(X))/np.sqrt(1+slope*slope)
    attrs={'riparian':np.exp(-((dist-112)/65)**2)}
    valley_mat=mat_ground('valley_ground',C['far_a'],C['far_b'],.024)
    nt=valley_mat.node_tree; bs=L.bsdf_of(valley_mat)
    at=nt.nodes.new('ShaderNodeAttribute'); at.attribute_name='riparian'
    old=bs.inputs['Base Color'].links[0].from_socket
    nt.links.new(L.mix_rgb(nt,old,L.srgb('#315c38'),L.math_node(nt,'MULTIPLY',at.outputs['Fac'],.92)),bs.inputs['Base Color'])
    add('far',L.mesh_from_grid('valley',X,Y,terrain(X,Y),attrs,valley_mat))
    xs=80+149920*np.linspace(0,1,1700)**3.1
    X=np.broadcast_to(xs[None,:],(35,len(xs))).copy()
    channel=moab_channel(X)
    width=(65+18*np.sin(X/95)+20*noise(X,X*0,120,16,73)
           +12*np.sin(X/37+.7))
    slope=(moab_channel(X+1)-moab_channel(X-1))*.5
    norm=np.sqrt(1+slope*slope)
    across=np.linspace(-1,1,35)[:,None]*width
    # 河寬沿中心線的法向展開，不能固定沿世界 Y 擠出。後者在大彎處
    # 會沿流向拉成尖三角，並在透視下製造長而直的岸線。
    Y=channel+across/norm
    X=X-across*slope/norm
    Z=np.zeros_like(X)+(2-terrain_origin+.5)
    stream_mat=mat_ground('valley_water','#285d73','#55969b',.06,water=True)
    L.bsdf_of(stream_mat).inputs['Roughness'].default_value=.4
    L.bsdf_of(stream_mat).inputs['Specular IOR Level'].default_value=.35
    add('far',L.mesh_from_grid('valley_stream',X,Y,Z,None,stream_mat))
elif a.scene in ('east','esau-jacob'):
    # 同一份頂點與法線密度。遠景延伸到鏡頭後，中景的末端在後製漸隱，
    # 不把網格的直線終點當地形輪廓；兩層可獨立移動但仍有足夠重疊。
    X,Y=grid(-90,150000,1050,920,3.2)
    Z=terrain(X,Y)
    attrs={}
    if a.scene=='esau-jacob':
        cy=-.46*X+100*np.sin(X/650)+35
        attrs['road']=np.exp(-((Y-cy)/(3+X*.009))**2)*L.smoothstep(50,200,X)
    add('far',L.mesh_from_grid('far_land',X,Y,Z,attrs,ground))
    end=int(np.searchsorted(X[0],7200))
    add('mid',L.mesh_from_grid('mid_land',X[:,:end],Y[:,:end],Z[:,:end],
                              {k:v[:,:end] for k,v in attrs.items()},ground))
else:
    X,Y=grid(-90,3800,500,540,2.4)
    Z=terrain(X,Y)
    attrs={}
    if a.scene=='esau-jacob':
        cy=-.34*X+80*np.sin(X/1400)
        attrs['road']=np.exp(-((Y-cy)/(2+X*.012))**2)
    if a.scene=='canaan':
        attrs['terrace']=L.smoothstep(.02,.4,noise(X,Y,280,35,44))*(.5+.5*np.cos(Z*1.1))
    add('mid',L.mesh_from_grid('mid_land',X,Y,Z,attrs,ground))
    X,Y=grid(3300,150000,430,560,2.5)
    add('far',L.mesh_from_grid('far_land',X,Y,terrain(X,Y)-.03,None,far_mat))

# 近景不是面對相機的卡片：實體地表延伸到鏡頭後方，前端順坡沉入 mid。
# 依投影推算 crest 距離，確保地面上緣落在畫面高度約 82%。
near_lower={'moab':.12,'canaan':.2}.get(a.scene,0.)
near_z = C['camera']-2.5-near_lower
sensor_h=36.*a.h/a.w
crest=2.5/(.32*sensor_h/C['lens']-math.tan(math.radians(C['pitch'])))
NX,NY=grid(-40,crest+6,170,280,1.)
if a.scene in ('east','moab','esau-jacob','beyond-river'):
    NX,NY=grid(-40,crest+6,240,640,1.)
    # 舊扇形網格在十公尺內仍橫跨三百公尺，畫面只有幾個頂點。
    # 近景獨立取樣範圍，在視野外留餘幅並保有足夠輪廓細節。
    NY=np.linspace(-1,1,640)[:,None]*(np.maximum(NX,0)+12)*1.4
crest_j=crest+.7*noise(NY,NY*0,12,1.5,60)
NZ=near_z+.08*(NX-crest_j)+.14*noise(NX,NY,7,.6,61)
if a.scene in ('east','moab','esau-jacob','beyond-river'):
    NZ+=.32*noise(NY,NY*0,2.7,.3,67)+.16*np.sin(NY*2.1+.5)
NZ-=L.smoothstep(crest_j,crest_j+6,NX)*5
add('near',L.mesh_from_grid('near_ground',NX,NY,NZ,None,near_mat))

rock_meshes=[]
for k in range(6):
    bm=bmesh.new()
    scales=(rng.uniform(.7,2.1),rng.uniform(.65,1.4),rng.uniform(.35,.95)) if a.scene=='moab' else (1.5,1.,.55)
    L.sphere_bm(1.,(0,0,.22),scales,3 if a.scene=='moab' and k%2==0 else 2,bm,noise=.4 if a.scene=='moab' else .32,seed=k+22)
    me=bpy.data.meshes.new('rock_mesh_'+str(k)); bm.to_mesh(me); bm.free(); me.materials.append(near_mat)
    rock_meshes.append(me)
ng=L.Ground([objs['near'][0]])
for i in range(28 if a.scene!='moab' else 45):
    x=rng.uniform(crest-4,crest+.3); y=rng.uniform(-13,13)
    z=ng.z(x,y)
    if z is not None:
        add('near',L.instance(rng.choice(rock_meshes),'foreground_rock_'+str(i),(x,y,z-.18),rot_z=rng.uniform(0,6.28),scale=rng.uniform(.17,.72)))

def reeds(pl, ground_query, count, x0, x1, yspan, scale=1.):
    bm=bmesh.new()
    for i in range(11):
        ang=rng.uniform(0,6.28); h=rng.uniform(.4,1.5)
        dx,dy=math.cos(ang),math.sin(ang)
        L.tube_bm([(dx*.1,dy*.1,0),(dx*.17,dy*.17,h*.65),(dx*.36,dy*.36,h)],[.012,.008,.001],3,bm)
    me=bpy.data.meshes.new(pl+'_grass_mesh'); bm.to_mesh(me); bm.free()
    me.materials.append(L.pbr(pl+'_grass','#41462b',.95))
    for i in range(count):
        x=rng.uniform(x0,x1); y=rng.uniform(-yspan,yspan); z=ground_query.z(x,y)
        if z is not None: add(pl,L.instance(me,pl+'_grass_'+str(i),(x,y,z-.03),rot_z=rng.uniform(0,6.28),scale=scale*rng.uniform(.45,1.1)))

if a.scene in ('beyond-river','isaac','jordan','canaan'):
    reeds('near',ng,65,crest-2,crest+.3,15,.45 if a.scene=='isaac' else .7)
if a.scene=='jordan':
    reeds('far',L.Ground([bank_ob]),150,C['bank']+1,C['bank']+25,180,1.8)
    bm=bmesh.new()
    L.tube_bm([(0,0,0),(.1,0,3.7)],[.15,.08],6,bm)
    for k in range(5):
        L.sphere_bm(1.5,(rng.uniform(-1.2,1.2),rng.uniform(-1.2,1.2),3.6+rng.uniform(-.4,.7)),(1.3,1.,.9),2,bm,noise=.3,seed=k+65)
    tree=bpy.data.meshes.new('oasis_tree_mesh'); bm.to_mesh(tree); bm.free(); tree.materials.append(L.pbr('oasis_leaves','#4d6038',.95))
    fg=L.Ground([bank_ob])
    for i in range(170):
        y=rng.uniform(-370,370); x=C['bank']+rng.uniform(25,260)
        if math.sin(y*.038)+math.cos(x*.04)<.2: continue
        z=fg.z(x,y)
        if z is not None: add('far',L.instance(tree,'oasis_'+str(i),(x,y,z),rot_z=rng.uniform(0,6.28),scale=rng.uniform(.6,1.2)))
if a.scene=='isaac':
    reeds('mid',L.Ground([objs['mid'][0]]),200,15,160,80,.32)

# 埃及只加植物：棕櫚以枝葉網格組成，稀疏成叢，避免均勻柵欄。
if a.scene=='egypt':
    bm=bmesh.new()
    L.tube_bm([(0,0,0),(.3,0,5.5),(.65,.1,10)],[.19,.13,.09],7,bm)
    for j in range(10):
        ang=j*math.tau/10
        dx,dy=math.cos(ang),math.sin(ang)
        L.tube_bm([(.65,.1,10),(.65+dx*1.4,.1+dy*1.4,10.6),(.65+dx*3.,.1+dy*3.,9.5)],[.12,.19,.005],4,bm)
        for k in range(1,7):
            t=k/7; px=.65+dx*3*t; py=.1+dy*3*t; pz=10+.9*math.sin(t*math.pi)-.5*t
            for side in (-1,1):
                L.tube_bm([(px,py,pz),(px-dy*.6*side+dx*.35,py+dx*.6*side+dy*.35,pz-.7)],[.065,.002],3,bm)
    palm=L.mesh_obj('palm_template',bm,L.pbr('palm','#343c37',.95)); palm.hide_render=True
    fg=L.Ground([bank_ob])
    for cluster,cy in enumerate((-200,-145,80,150,320)):
        for i in range(rng.randint(3,6)):
            x=C['bank']+rng.uniform(8,55); y=cy+rng.uniform(-15,15); z=fg.z(x,y)
            if z is not None: add('far',L.instance(palm.data,'palm_%s_%s'%(cluster,i),(x,y,z),rot_z=rng.uniform(0,6.28),scale=rng.uniform(.8,1.3)))

cam=L.set_camera((0,0,C['camera']),(100,0,C['camera']),lens=C['lens'],clip=(.1,2e6))
cam.rotation_euler=(math.pi/2+math.radians(C['pitch']),0,-math.pi/2)
L.render_settings(a.w,a.h,a.samples,raytrace=True)

def emission(name,color,strength):
    m=L.new_mat(name); nt=m.node_tree; nt.nodes.clear()
    em=nt.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value=(*color,1); em.inputs['Strength'].default_value=strength
    out=nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(em.outputs[0],out.inputs['Surface'])
    return m

# 星與月為 Blender 天空幾何；確定性 seed。銀河為世界方向雜訊發光帶。
if C['stars']:
    nt=w.node_tree
    bg=next(n for n in nt.nodes if n.type=='BACKGROUND')
    old=bg.inputs['Color'].links[0].from_socket
    tc=nt.nodes.new('ShaderNodeTexCoord'); sep=nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Generated'],sep.inputs[0])
    band_axis=L.math_node(nt,'ADD',L.math_node(nt,'ADD',sep.outputs['Y'],L.math_node(nt,'MULTIPLY',sep.outputs['Z'],.72)),.06)
    band=L.math_node(nt,'EXPONENT',L.math_node(nt,'MULTIPLY',L.math_node(nt,'MULTIPLY',band_axis,band_axis),-95))
    n=L.noise_tex(nt,tc.outputs['Generated'],15.,6.,.7)
    bright=L.math_node(nt,'MULTIPLY',band,L.math_node(nt,'MULTIPLY',n,.32))
    col=L.mix_rgb(nt,(0,0,0),(.65,.72,.9),bright,blend='ADD')
    nt.links.new(L.mix_rgb(nt,old,col,1.,blend='ADD'),bg.inputs['Color'])
    star_mat=emission('starlight',(.7,.8,1.),3.)
    verts=[]; faces=[]
    # 星點直接在鏡頭座標均勻分布，月以下的地形自然遮擋。
    q=cam.rotation_euler.to_quaternion()
    for i in range(4400):
        sx=rng.uniform(-.85,.85); sy=rng.uniform(-.48,.48)
        if i>=3400: sx=.72*sy+.06+rng.gauss(0,.05)
        center=cam.location+q@Vector((sx*8000,sy*8000,-8000))
        size=rng.choices((1.7,2.6,4.,5.6),(.55,.3,.13,.02))[0]
        right=q@Vector((size,0,0)); up=q@Vector((0,size,0))
        idx=len(verts); verts.extend([center-right-up,center+right-up,center+right+up,center-right+up]); faces.append((idx,idx+1,idx+2,idx+3))
    me=bpy.data.meshes.new('starfield'); me.from_pydata(verts,[],faces); add('sky',L.mesh_obj('stars',me,star_mat,smooth=False))
if C['moon']:
    # 小月盤，細微月海由材質噪訊控制；不製造大片泛白光暈。
    moonmat=emission('moonlight',(.66,.76,.94),2.)
    nt=moonmat.node_tree; em=next(n for n in nt.nodes if n.type=='EMISSION')
    tc=nt.nodes.new('ShaderNodeTexCoord'); nz=L.noise_tex(nt,tc.outputs['Generated'],7.,4.,.7)
    nt.links.new(L.mix_rgb(nt,(.28,.39,.57),(.8,.86,1.),nz),em.inputs['Color'])
    q=cam.rotation_euler.to_quaternion(); center=cam.location+q@Vector((2600,1900,-8000))
    bm=bmesh.new(); L.sphere_bm(50,tuple(center),(1,1,1),3,bm)
    add('sky',L.mesh_obj('moon',bm,moonmat))

build_seconds=time.perf_counter()-started
timings=dict(previous.get('plates_seconds',{}))
for plate in ('sky','far','mid','near'):
    if a.only and plate not in a.only: continue
    for group in objs.values():
        for ob in group: ob.hide_render=True
    for ob in objs[plate]: ob.hide_render=False
    sc.render.film_transparent=plate!='sky'
    t=time.perf_counter()
    if plate in ('far','mid'):
        L.render_pair(os.path.join(a.out,plate),sun_dir=sund,depth_samples=4,y_pass=False)
    else:
        L.render_to(os.path.join(a.out,plate))
    timings[plate]=round(time.perf_counter()-t,3)
meta=dict(scene=a.scene,res=[a.w,a.h],samples=a.samples,paint_choice=S.PAINT_CHOICE,paint_amount=S.PAINT[S.PAINT_CHOICE]['amount'],config=C,near_lower=near_lower,plates_seconds=timings,total_seconds=round(build_seconds+sum(timings.values()),3))
with open(os.path.join(a.out,'meta.json'),'w',encoding='utf-8') as f: json.dump(meta,f,indent=2)
print('STATION_COMPLETE',json.dumps(meta))
