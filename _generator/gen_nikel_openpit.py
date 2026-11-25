"""
gen_nikel_openpit.py - dataset sintetis OPEN PIT NIKEL LATERIT ("Lamonto Block Model").
Pasangan model blok + permukaan topografi untuk dataset bor `02-nikel-laterit`.
Analog gaya endapan: laterit atas ultramafik, Sulawesi Tenggara / Halmahera (UTM 51S).
Semua angka dihasilkan model, bukan data nyata.

Keluaran di 05-nikel-laterit-open-pit/:
  - surface_topo.dxf : topografi perbukitan laterit (3DFACE R12 ASCII)
  - surface_topo.csv : grid titik topografi X,Y,Z
  - block_model.csv  : model blok 3D 25x25x2 m (OVB/LIM/SAP/BRK + kelas JORC)
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import SmoothNoise, write_surface_csv, write_surface_dxf

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "05-nikel-laterit-open-pit")
SEED = 20260830
CRS = "EPSG:32751"
VDATUM = "MSL"

rng = np.random.default_rng(SEED)

# Memakai asal koordinat & parameter medan geologi yang konsisten dengan gen_nikel.py
X0, Y0 = 392000.0, 9558000.0
EX, EY = 1900.0, 1500.0

topo_n = SmoothNoise(rng, (0, 0), (EX + 400, EY + 400), 560, 2, 2)
brk_n = SmoothNoise(rng, (0, 0), (EX + 400, EY + 400), 300, 3, 2)
lim_n = SmoothNoise(rng, (0, 0), (EX + 400, EY + 400), 380, 3, 2)
sap_n = SmoothNoise(rng, (0, 0), (EX + 400, EY + 400), 340, 3, 2)
rich_n = SmoothNoise(rng, (0, 0), (EX + 400, EY + 400), 430, 2, 2)

ANIS = 42.0
g3 = SmoothNoise(rng, (0, 0, -1500), (EX + 400, EY + 400, 3000), 170, 2, 3)


def topo(lx, ly):
    """Topografi perbukitan laterit pada koordinat lokal (lx, ly)."""
    return 300.0 + 34.0 * topo_n(lx, ly) + 0.011 * ly - 0.006 * lx


def slope_pct(lx, ly, h=25.0):
    dzx = (topo(lx + h, ly) - topo(lx - h, ly)) / (2 * h)
    dzy = (topo(lx, ly + h) - topo(lx, ly - h)) / (2 * h)
    return 100.0 * np.sqrt(dzx ** 2 + dzy ** 2)


def profile(lx, ly):
    sl = slope_pct(lx, ly)
    dev = np.clip(1.30 - 0.021 * sl, 0.40, 1.30)
    t_ovb = np.clip(1.3 + 0.55 * brk_n(lx, ly), 0.3, 3.0)
    t_lim = np.clip((8.1 + 3.6 * lim_n(lx, ly)) * dev, 0.8, 19.0)
    t_sap = np.clip((13.6 + 5.6 * sap_n(lx, ly)) * dev, 1.0, 28.0)
    return t_ovb, t_lim, t_sap


ENDS = {
    "OVB": ((0.52, 0.030, 50.5, 0.50, 2.6, 1.55),
            (0.86, 0.055, 48.5, 1.10, 5.2, 1.55)),
    "LIM": ((0.92, 0.062, 47.0, 1.40, 6.5, 1.42),
            (1.38, 0.105, 37.5, 6.20, 17.5, 1.52)),
    "SAP": ((2.35, 0.055, 21.0, 9.5, 32.0, 1.48),
            (1.05, 0.022, 9.5, 27.5, 41.5, 1.85)),
    "BRK": ((0.30, 0.014, 6.8, 36.5, 40.0, 2.62),
            (0.26, 0.012, 6.2, 39.5, 41.0, 2.68)),
}
ELEM = ["NI", "CO", "FE", "MGO", "SIO2", "SG"]
RELSD = dict(NI=0.11, CO=0.18, FE=0.06, MGO=0.09, SIO2=0.07, SG=0.05)

# Cakupan penambangan 1.150 x 950 m berpusat di blok infill 50 m (lx: 700..1100, ly: 600..1000)
DX, DY, DZ = 25.0, 25.0, 2.0
LX_START, NX = 325.0, 46               # 325 .. 1475 m (1.150 m)
LY_START, NY = 325.0, 38               # 325 .. 1275 m (950 m)

# ------------------------------------------------------------------ 1. topografi
tx = X0 + np.arange(LX_START - 50.0, LX_START + NX * DX + 50.1, 25.0)
ty = Y0 + np.arange(LY_START - 50.0, LY_START + NY * DY + 50.1, 25.0)
mx_t, my_t = np.meshgrid(tx - X0, ty - Y0, indexing="ij")
gz_t = topo(mx_t, my_t)

os.makedirs(OUT, exist_ok=True)
dxf_path = os.path.join(OUT, "surface_topo.dxf")
csv_topo_path = os.path.join(OUT, "surface_topo.csv")
n_faces = write_surface_dxf(dxf_path, tx, ty, gz_t, layer="TOPOGRAPHY", crs=CRS, vertical_datum=VDATUM)
write_surface_csv(csv_topo_path, tx, ty, gz_t, crs=CRS, vertical_datum=VDATUM)

# ------------------------------------------------------------------ 2. grid 3D block model
lxs = LX_START + (np.arange(NX) + 0.5) * DX
lys = LY_START + (np.arange(NY) + 0.5) * DY
m_lx, m_ly = np.meshgrid(lxs, lys, indexing="ij")
col_zt = topo(m_lx, m_ly)
col_ovb, col_lim, col_sap = profile(m_lx, m_ly)
col_brk_top = col_zt - (col_ovb + col_lim + col_sap)

z_min_c = np.floor((col_brk_top.min() - 10.0) / DZ) * DZ + 1.0
z_max_c = np.ceil((col_zt.max() + DZ) / DZ) * DZ + 1.0
zs = np.arange(z_min_c, z_max_c + 0.1, DZ)

gx, gy, gz = np.meshgrid(lxs, lys, zs, indexing="ij")
lx = gx.ravel()
ly = gy.ravel()
z = gz.ravel()

zt = topo(lx, ly)
t_ovb, t_lim, t_sap = profile(lx, ly)
b_ovb = t_ovb
b_lim = b_ovb + t_lim
b_sap = b_lim + t_sap

depth = zt - z
# Simpan 1 jenjang udara di atas topo dan minimal 8 m bedrock di bawah saprolit agar pit menutup bersih
keep = (z <= zt + DZ) & (depth <= b_sap + 10.0)
lx, ly, z, zt = lx[keep], ly[keep], z[keep], zt[keep]
b_ovb, b_lim, b_sap, t_lim, t_sap = b_ovb[keep], b_lim[keep], b_sap[keep], t_lim[keep], t_sap[keep]
depth = zt - z
is_air = z > zt

unit = np.where(
    depth < b_ovb, "OVB",
    np.where(depth < b_lim, "LIM", np.where(depth < b_sap, "SAP", "BRK")),
)

rel = np.zeros_like(depth)
rel = np.where(unit == "OVB", np.maximum(depth, 0.0) / np.maximum(b_ovb, 1e-6), rel)
rel = np.where(unit == "LIM", (depth - b_ovb) / np.maximum(t_lim, 1e-6), rel)
rel = np.where(unit == "SAP", (depth - b_lim) / np.maximum(t_sap, 1e-6), rel)
rel = np.where(unit == "BRK", np.clip((depth - b_sap) / 8.0, 0.0, 1.0), rel)
rel = np.clip(rel, 0.0, 1.0)

n3 = g3(lx, ly, z * ANIS)
rich = rich_n(lx, ly)
# Pengayaan saprolit terkonsentrasi alami di zona tengah (900, 800) agar batas pit ekonomis menutup di dalam grid
lobe = np.exp(-0.5 * (((lx - 900.0) / 260.0) ** 2 + ((ly - 800.0) / 220.0) ** 2))

vals = {}
for k, e in enumerate(ELEM):
    lo = np.array([ENDS[u][0][k] for u in unit])
    hi = np.array([ENDS[u][1][k] for u in unit])
    base = lo + (hi - lo) * rel
    if e == "NI":
        # Zona tepi agak miskin (~0.75-0.95% Ni) sehingga pit menutup ekonomis di dalam blok model
        factor = (0.58 + 0.56 * lobe) * (1.0 + 0.12 * rich)
        base = np.where(unit == "BRK", base, base * factor)
    noise = 1.0 + RELSD[e] * (0.75 * n3 + 0.66 * rng.standard_normal(lx.size))
    vals[e] = np.clip(base * noise, 0.0, None)

co_spike = 1.0 + 1.7 * np.exp(-0.5 * ((depth - b_lim) / 1.4) ** 2)
vals["CO"] = vals["CO"] * co_spike

vals["FE"] = np.clip(vals["FE"], 3.0, 56.0)
vals["MGO"] = np.clip(vals["MGO"], 0.2, 45.0)
vals["NI"] = np.where(is_air, 0.10, np.clip(vals["NI"], 0.05, 4.2))
vals["SG"] = np.clip(vals["SG"], 1.25, 2.80)

# Klasifikasi JORC/KCMI mengikuti kerapatan bor: 50 m infill -> Measured, 100 m -> Indicated, luar -> Inferred
rclass = np.where(
    is_air | (lx < 480.0) | (lx > 1320.0) | (ly < 460.0) | (ly > 1140.0),
    "Inferred",
    np.where((lx >= 680.0) & (lx <= 1120.0) & (ly >= 580.0) & (ly <= 1020.0), "Measured", "Indicated"),
)

df = pd.DataFrame({
    "X": np.round(X0 + lx, 2),
    "Y": np.round(Y0 + ly, 2),
    "Z": np.round(z, 2),
    "DX": DX,
    "DY": DY,
    "DZ": DZ,
    "DENSITY": np.round(vals["SG"], 3),
    "DOMAIN": unit,
    "CLASS": rclass,
    "NI_PCT": np.round(vals["NI"], 3),
    "CO_PCT": np.round(vals["CO"], 4),
    "FE_PCT": np.round(vals["FE"], 2),
    "MGO_PCT": np.round(vals["MGO"], 2),
    "SIO2_PCT": np.round(vals["SIO2"], 2),
})

bm_path = os.path.join(OUT, "block_model.csv")
with open(bm_path, "w", encoding="utf-8", newline="\n") as fh:
    fh.write(f"# Orebit Synthetic Nickel Laterite Block Model | CRS: {CRS} | VERTICAL_DATUM: {VDATUM}\n")
    df.to_csv(fh, index=False)

below = df[~is_air]
sap = below[below["DOMAIN"] == "SAP"]
print(f"DXF triangles : {n_faces:,} ({os.path.getsize(dxf_path):,} bytes)")
print(f"Total blocks  : {len(df):,} (air above topo: {int(is_air.sum()):,}, rock below topo: {len(below):,})")
print(f"Topo Z range  : {gz_t.min():.1f} .. {gz_t.max():.1f} m RL")
print(f"Domains (rock): {below['DOMAIN'].value_counts().to_dict()}")
print(f"Classes (rock): {below['CLASS'].value_counts().to_dict()}")
print(f"SAP Ni        : n={len(sap):,}, mean={sap['NI_PCT'].mean():.2f}%, med={sap['NI_PCT'].median():.2f}%, max={sap['NI_PCT'].max():.2f}%, CV={sap['NI_PCT'].std()/sap['NI_PCT'].mean():.2f}")
print(f"Fe vs MgO r   : {below['FE_PCT'].corr(below['MGO_PCT']):.3f}")
