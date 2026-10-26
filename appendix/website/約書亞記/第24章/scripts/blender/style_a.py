"""風格 A「史詩剪影」的燈光、天空、霧、色調與相機設定（整段渲染照這份做）。

兩端共用：
  - Blender 端：`import style_a as S; S.world("cover", sun_az=...)` 建天空、太陽與補光。
  - 驅動與後製端：`S.POST["cover"]` 是 epic_post.py 風格 A 的參數；`S.SIZE` 是輸出尺寸。

風格要點（使用者 2026-10-26 選定）：
  人物很小、天地很大；低角度日光（太陽離地平線 5–15 度）；體積光束（螢幕空間放射模糊，只在太陽朝向鏡頭的畫面）；
  大氣透視（遠景融進天空色，霧色取自地平線上緣的天空）；谷地薄霧（依世界高度）；人物以輪廓為主。
  色調：暖橘高光、偏冷紫藍暗部（分色），飽和度略降，暗角，輕微顆粒。
"""
import math

SIZE = (1280, 720)
SAMPLES = 32

# ---- 天空與光：每個場景一組（setup_world 的參數；sun_az 由場景決定，因為要對齊谷軸或河流） ----
LIGHT = {
    # 示劍山谷清晨：太陽在谷口，剛離地平線，被橡樹冠遮住一角
    "cover": dict(sun_el=7.5, sun_energy=6.5, sun_color=(1.0, 0.76, 0.5), glow_k=0.8, glow="#ffc58e", disc_k=400.0, disc_deg=1.4,
                  horizon="#eab991", mid="#a8b5d0", zenith="#4a6492", ground="#7a6552", strength=1.0,
                  clouds=0.9, cloud_scale=1.6, cloud_seed=3.0, fill=2.4, fill_color=(1.0, 0.78, 0.56)),
    # 紅海：黎明在鏡頭後方，前方是壓低的暗雲；水牆被曙光照亮
    "redsea": dict(sun_el=15.0, sun_energy=5.5, sun_color=(1.0, 0.8, 0.6), glow_k=0.35, glow="#ffcf9a", disc_k=60.0, disc_deg=1.2,
                   horizon="#d3a58f", mid="#6c7597", zenith="#262e4e", ground="#2b2b34", strength=0.9,
                   clouds=1.0, cloud_scale=2.0, cloud_seed=7.0, fill=2.2, fill_color=(1.0, 0.86, 0.72)),
    # 幼發拉底河：清晨斜光，河面反光，空氣乾燥微塵
    "river": dict(sun_el=9.0, sun_energy=6.0, sun_color=(1.0, 0.78, 0.55), glow_k=0.9, glow="#ffc58e", disc_k=300.0, disc_deg=1.3,
                  horizon="#efc29c", mid="#a9b8d2", zenith="#4d6a9c", ground="#7a6a58", strength=1.0,
                  clouds=0.7, cloud_scale=1.8, cloud_seed=11.0, fill=2.2, fill_color=(1.0, 0.8, 0.6)),
    # 迦南黃昏：太陽剛沉，天空青紫，地上的光一處處亮起
    # 2.5D 背景圖層（紅海、渡口）：黎明，太陽剛離地平線，鏡頭在西岸往東看（太陽在正前方偏左）
    "plate_dawn": dict(sun_el=2.6, sun_energy=5.0, sun_color=(1.0, 0.72, 0.48), glow_k=1.5, glow="#ffb878", disc_k=500.0, disc_deg=1.5,
                       horizon="#f2b98e", mid="#a7a3c4", zenith="#3e4f85", ground="#c79a82", strength=1.0,
                       clouds=0.95, cloud_scale=1.5, cloud_seed=9.0, fill=0.8, fill_color=(1.0, 0.75, 0.6)),
    # 紅海西望版：鏡頭在東岸，太陽在鏡頭後方（畫面裡沒有日盤）；前方是黎明前的靛藍天空，地平線一帶轉玫瑰與琥珀
    "plate_west": dict(sun_el=-2.0, sun_energy=0.5, sun_color=(1.0, 0.7, 0.55), glow_k=0.0, glow="#ffb090", disc_k=0.0, disc_deg=1.0,
                       horizon="#f6b08c", mid="#a77da4", zenith="#1c2658", ground="#e29b80", strength=1.25,
                       clouds=1.0, cloud_scale=1.4, cloud_seed=14.0, fill=0.35, fill_color=(1.0, 0.7, 0.62), cloud_lit=0.95),
    "canaan": dict(sun_el=2.5, sun_energy=1.3, sun_color=(1.0, 0.7, 0.52), glow_k=0.9, glow="#ff9a5a", disc_k=0.0, disc_deg=1.2,
                   horizon="#f0a173", mid="#6a6f9c", zenith="#1d2a55", ground="#a87a68", strength=0.9,
                   clouds=0.8, cloud_scale=1.7, cloud_seed=5.0, fill=2.4, fill_color=(0.55, 0.6, 0.95)),
}

# ---- 後製參數（epic_post.py 風格 A；dark 只用在紅海） ----
DARK_REDSEA = {"xc": -95, "core": 12, "soft": 28, "k": 1.15, "behind": 0.55, "warp": 55.0}

POST = {
    "cover": {"haze_gain": 0.9, "haze_mix": 0.8, "haze_dist": 4800, "mist_z0": 790, "mist_rho": 0.005, "mist_H": 140, "ray_gain": 3.2, "ray_len": 0.75, "ray_soft": 14.0,
              "ray_max": 0.5, "exposure": 0.85, "sat": 0.9, "vig": 0.6, "bloom": 0.7},
    "redsea": {"dark": DARK_REDSEA, "haze_dist": 16000, "haze_gain": 1.0, "haze_mix": 0.8, "mist_rho": 0, "exposure": 1.5},
    "river": {"hdr_cap": 9.0, "haze_dist": 42000, "haze_gain": 1.0, "haze_mix": 0.6, "mist_z0": 900, "mist_rho": 0.0012, "mist_H": 90,
              "ray_gain": 2.0, "ray_len": 0.7, "ray_max": 0.5, "exposure": 0.85, "sat": 1.0, "vig": 0.6, "bloom": 0.7},
    "canaan": {"zcap": 700000.0, "haze_dist": 420000, "haze_gain": 1.0, "haze_mix": 0.6, "mist_rho": 0, "exposure": 1.7, "sat": 0.85, "vig": 0.6, "bloom": 1.1,
               "bloom_thr": 0.7, "shadows": (0.9, 0.95, 1.2), "highs": (1.2, 1.0, 0.8)},
}


# ---- A+C：在 A 之上疊一層輕的繪本質感（使用者 2026-10-26：以 A 為主，融入一點 C）。
#   amount 總強度 0..1；kuwahara 色塊半徑（像素）；strokes 筆觸層強度；levels 柔性色階（越小越簡化）；
#   edge_soft 邊緣柔化；paper 紙紋與顏料顆粒；warm 暖色繪本色盤。PAINT_CHOICE 設成 "light"/"medium"/"strong" 就會套用到所有畫格。
PAINT = {
    "light": dict(amount=0.35, kuwahara=2, strokes=0.45, levels=16, edge_soft=0.5, edge_px=1.0, paper=0.05, warm=0.30),
    "medium": dict(amount=0.6, kuwahara=3, strokes=0.65, levels=13, edge_soft=0.6, edge_px=1.2, paper=0.06, warm=0.38),
    "strong": dict(amount=0.85, kuwahara=4, strokes=0.8, levels=10, edge_soft=0.7, edge_px=1.4, paper=0.07, warm=0.45),
}
# 「chosen」：使用者選定的強度 0.45（介於 light 0.35 與 medium 0.60 之間，其餘參數按比例內插）
PAINT["chosen"] = dict(amount=0.45, kuwahara=2, strokes=0.53, levels=15, edge_soft=0.54, edge_px=1.08, paper=0.054, warm=0.332)
PAINT_CHOICE = "chosen"


def post_params(name, paint=None):
    """回傳某畫格的後製參數（含繪畫層，若有選）。paint 為 None 時用 PAINT_CHOICE。"""
    p = dict(POST[name])
    choice = paint if paint is not None else PAINT_CHOICE
    if choice:
        p["paint"] = dict(PAINT[choice])
    return p


def world(name, sun_az, **over):
    """建立天空、太陽燈與補光。sun_az 為太陽方位（數學角，0 = 東、90 = 北、180 = 西、270 = 南）。"""
    import epic_lib as L

    cfg = dict(LIGHT[name])
    cfg.update(over)
    el = cfg.pop("sun_el")
    return L.setup_world(el, sun_az, **cfg)


def camera_height_hint():
    return "封面 6.5 m；紅海 22 m；河邊 8 m；迦南高空 40 km"
