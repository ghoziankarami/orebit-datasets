"""
gen_emas_openpit.py - dataset sintetis OPEN PIT EMAS ("Gunung Kencana").
Analog gaya endapan: epithermal high/intermediate-sulphidation / porphyry-stockwork
terbuka di Indonesia (Martabe / Tujuh Bukit / Awak Mas sebagai analog gaya).
Semua angka dihasilkan model, bukan data nyata.

Keluaran di 04-emas-open-pit/:
  - surface_topo.dxf : topografi punggungan & lembah vulkanik (3DFACE R12 ASCII)
  - surface_topo.csv : grid titik topografi X,Y,Z (untuk fallback non-DXF)
  - block_model.csv  : model blok 3D 15x15x10 m (OXIDE/TRANS/FRESH + kelas JORC)
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import D2R, SmoothNoise, write_surface_csv, write_surface_dxf

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "04-emas-open-pit")
SEED = 20261125
CRS = "EPSG:32748"
VDATUM = "MSL"

rng = np.random.default_rng(SEED)

# ------------------------------------------------------------------ geometri
# UTM 48S, grid 15 x 15 x 10 m, cakupan 1.050 x 1.050 m (70 x 70 kolom)
X0, Y0 = 520000.0, 9180000.0
DX, DY, DZ = 15.0, 15.0, 10.0
NX, NY = 70, 70
Z_MIN_C, Z_MAX_C = 175.0, 445.0        # 28 jenjang: dasar 170 m .. puncak 450 m

CX, CY, CZ = X0 + 525.0, Y0 + 525.0, 325.0
STRIKE, DIP = 330.0, 70.0              # jurus N30W, dip 70 deg ke ENE (060)

s_hat = np.array([np.sin(STRIKE * D2R), np.cos(STRIKE * D2R), 0.0])
dipdir = (STRIKE + 90.0) * D2R
d_hat = np.array([
    np.sin(dipdir) * np.cos(DIP * D2R),
    np.cos(dipdir) * np.cos(DIP * D2R),
    -np.sin(DIP * D2R),
])
d_hat /= np.linalg.norm(d_hat)
n_hat = np.cross(s_hat, d_hat)
n_hat /= np.linalg.norm(n_hat)
P0 = np.array([CX, CY, CZ])

# ------------------------------------------------------------------ medan geologi
topo_n = SmoothNoise(rng, (X0 - 200, Y0 - 200), (1500, 1500), 340, 3, 2)
wx_ox_n = SmoothNoise(rng, (X0 - 200, Y0 - 200), (1500, 1500), 220, 2, 2)
wx_tr_n = SmoothNoise(rng, (X0 - 200, Y0 - 200), (1500, 1500), 240, 2, 2)
swell_n = SmoothNoise(rng, (-500, -300), (1000, 600), 140, 2, 2)
au_3d = SmoothNoise(rng, (X0 - 100, Y0 - 100, 120), (1300, 1300, 380), 42, 3, 3)
ag_3d = SmoothNoise(rng, (X0 - 100, Y0 - 100, 120), (1300, 1300, 380), 55, 2, 3)
den_3d = SmoothNoise(rng, (X0 - 100, Y0 - 100, 120), (1300, 1300, 380), 90, 2, 3)


def topo(x, y):
    """Topografi punggungan vulkanik ~275-425 m RL (relief ~150 m)."""
    dx = (x - CX) / 360.0
    dy = (y - CY) / 420.0
    ridge = 62.0 * np.exp(-0.5 * ((0.85 * dx + 0.35 * dy) ** 2 + (0.4 * dy) ** 2))
    valley = -28.0 * np.exp(-0.5 * (((x - (CX + 290.0)) / 180.0) ** 2 + ((y - (CY - 120.0)) / 240.0) ** 2))
    slope = -0.025 * (x - CX) + 0.015 * (y - CY)
    return 338.0 + ridge + valley + slope + 24.0 * topo_n(x, y)


def weathering_depths(x, y):
    """Kedalaman batas bawah OXIDE dan TRANS di bawah topografi (m)."""
    d_ox = np.clip(28.0 + 7.5 * wx_ox_n(x, y), 16.0, 44.0)
    d_tr = np.clip(d_ox + 22.0 + 8.0 * wx_tr_n(x, y), d_ox + 12.0, 74.0)
    return d_ox, d_tr


# ------------------------------------------------------------------ 1. permukaan topografi
tx = np.arange(X0 - 50.0, X0 + NX * DX + 60.1, 20.0)
ty = np.arange(Y0 - 50.0, Y0 + NY * DY + 60.1, 20.0)
mx_t, my_t = np.meshgrid(tx, ty, indexing="ij")
gz_t = topo(mx_t, my_t)

os.makedirs(OUT, exist_ok=True)
dxf_path = os.path.join(OUT, "surface_topo.dxf")
csv_topo_path = os.path.join(OUT, "surface_topo.csv")
n_faces = write_surface_dxf(dxf_path, tx, ty, gz_t, layer="TOPOGRAPHY", crs=CRS, vertical_datum=VDATUM)
write_surface_csv(csv_topo_path, tx, ty, gz_t, crs=CRS, vertical_datum=VDATUM)

# ------------------------------------------------------------------ 2. grid 3D block model
xs = X0 + (np.arange(NX) + 0.5) * DX
ys = Y0 + (np.arange(NY) + 0.5) * DY
zs = np.arange(Z_MIN_C, Z_MAX_C + 0.1, DZ)

gx, gy, gz = np.meshgrid(xs, ys, zs, indexing="ij")
x = gx.ravel()
y = gy.ravel()
z = gz.ravel()

zt = topo(x, y)
# Simpan hingga 2 jenjang (20 m) di atas topografi agar clip_to_surface teruji nyata
keep = z <= (zt + 2.0 * DZ)
x, y, z, zt = x[keep], y[keep], z[keep], zt[keep]

depth = np.maximum(0.0, zt - z)
d_ox, d_tr = weathering_depths(x, y)

domain = np.where(depth <= d_ox, "OXIDE", np.where(depth <= d_tr, "TRANS", "FRESH"))

# Koordinat lokal tubuh bijih (u=jurus, v=down-dip, w=tegak lurus bidang)
P = np.column_stack([x, y, z]) - P0
u = P @ s_hat
v = P @ d_hat
w = P @ n_hat

# Lebar zona mineralisasi utama (breksi/stockwork ~95-145 m) + halo stockwork
sw = swell_n(u, v)
half_w = 56.0 + 18.0 * sw
# Taper di ujung jurus (±230 m) & dasar (v > 125 m, agar pit menutup sempurna di dalam model)
taper_u = np.clip(1.0 - np.maximum(0.0, np.abs(u) - 165.0) / 85.0, 0.0, 1.0)
taper_v = np.clip(1.0 - np.maximum(0.0, v - 85.0) / 60.0, 0.0, 1.0)
env_strength = taper_u * taper_v

# Dua ore shoot menunjam di bidang utama
shoot1 = 0.85 * np.exp(-0.5 * (((u + 75.0) / 95.0) ** 2 + ((v + 10.0) / 70.0) ** 2))
shoot2 = 0.72 * np.exp(-0.5 * (((u - 95.0) / 85.0) ** 2 + ((v - 25.0) / 65.0) ** 2))
shoot = shoot1 + shoot2

# Profil kadar lognormal terkorelasi spasial (CV ~1.2-1.5 dalam tubuh bijih)
z_field = 0.78 * au_3d(x, y, z) + 0.62 * rng.standard_normal(x.size)
z_field = np.clip(z_field, -2.8, 3.0)

in_core = (env_strength > 0.15) & (np.abs(w) <= half_w * np.sqrt(env_strength))
dist_out = np.maximum(0.0, np.abs(w) - half_w * np.sqrt(np.maximum(env_strength, 1e-6)))
in_halo = (~in_core) & (env_strength > 0.10) & (dist_out <= 32.0)

# Inti bijih: rata-rata ~1.5 g/t Au, lognormal sigma ~0.85, top-cut <= 15 g/t
log_au_core = -0.15 + 0.68 * shoot + 0.55 * np.log(np.maximum(env_strength, 0.1)) + 0.78 * z_field
au_core = np.clip(np.exp(log_au_core), 0.05, 15.0)

# Halo stockwork: meluruh eksponensial menjauhi inti
au_halo = np.clip(0.55 * env_strength * np.exp(-dist_out / 16.0) * np.exp(0.58 * z_field), 0.01, 4.5)

# Batuan samping barren + buffer udara di atas topo
au_bg = np.clip(0.018 * np.exp(0.55 * rng.standard_normal(x.size)), 0.005, 0.08)

au = np.where(in_core, au_core, np.where(in_halo, au_halo, au_bg))
is_air = z > zt
au = np.where(is_air, 0.005, au)

# Ag berasosiasi ~6-10x Au di zona mineralisasi, latar rendah di waste
ag_ratio = 7.5 * np.exp(0.28 * ag_3d(x, y, z) + 0.22 * rng.standard_normal(x.size))
ag = np.where(in_core | in_halo, au * ag_ratio, np.clip(0.12 * np.exp(0.4 * rng.standard_normal(x.size)), 0.02, 0.8))
ag = np.where(is_air, 0.05, np.clip(ag, 0.02, 120.0))

# Densitas curah berdasar zona pelapukan + variasi spasial ringan
den_noise = 0.06 * den_3d(x, y, z) + 0.03 * rng.standard_normal(x.size)
density = np.select(
    [domain == "OXIDE", domain == "TRANS"],
    [np.clip(2.15 + den_noise, 1.92, 2.36), np.clip(2.45 + den_noise, 2.25, 2.62)],
    default=np.clip(2.68 + den_noise, 2.52, 2.86),
)

# Klasifikasi JORC/KCMI berdasarkan jarak ke pusat bor rapat & kedalaman
r_xy = np.hypot((x - CX) / 220.0, (y - CY) / 240.0)
r_inferred = np.hypot((x - CX) / 340.0, (y - CY) / 360.0)
rclass = np.where(
    is_air | (r_inferred > 1.0) | (z < 210.0),
    "Inferred",
    np.where((r_xy <= 0.72) & (z >= 250.0), "Measured", "Indicated"),
)

df = pd.DataFrame({
    "X": np.round(x, 2),
    "Y": np.round(y, 2),
    "Z": np.round(z, 2),
    "DX": DX,
    "DY": DY,
    "DZ": DZ,
    "DENSITY": np.round(density, 3),
    "DOMAIN": domain,
    "CLASS": rclass,
    "AU_GPT": np.round(au, 4),
    "AG_GPT": np.round(ag, 3),
})

bm_path = os.path.join(OUT, "block_model.csv")
with open(bm_path, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(f"# Orebit Synthetic Open-Pit Gold Block Model | CRS: {CRS} | VERTICAL_DATUM: {VDATUM}\n")
    df.to_csv(fh, index=False)

below = df[z <= zt]
ore_zone = below[below["AU_GPT"] >= 0.5]
print(f"DXF triangles : {n_faces:,} ({os.path.getsize(dxf_path):,} bytes)")
print(f"Total blocks  : {len(df):,} (air above topo: {int(is_air.sum()):,}, rock below topo: {len(below):,})")
print(f"Topo Z range  : {gz_t.min():.1f} .. {gz_t.max():.1f} m RL")
print(f"Domains (rock): {below['DOMAIN'].value_counts().to_dict()}")
print(f"Classes (rock): {below['CLASS'].value_counts().to_dict()}")
print(f"Au>=0.5 g/t   : n={len(ore_zone):,}, mean={ore_zone['AU_GPT'].mean():.2f}, med={ore_zone['AU_GPT'].median():.2f}, max={ore_zone['AU_GPT'].max():.2f}, CV={ore_zone['AU_GPT'].std()/ore_zone['AU_GPT'].mean():.2f}")
print(f"All rock Au   : mean={below['AU_GPT'].mean():.3f}, P90={below['AU_GPT'].quantile(0.9):.3f}, P99={below['AU_GPT'].quantile(0.99):.3f}")
