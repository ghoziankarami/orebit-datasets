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
from common import D2R, SmoothNoise, bilinear_surface_z, desurvey, write_surface_csv, write_surface_dxf

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

# ------------------------------------------------------------------ 3. drillholes (cross-app)
# Separate RNG created AFTER block_model.csv so block_model & surfaces remain bit-for-bit identical.
rng_dh = np.random.default_rng(SEED + 1001)


def eval_emas_field(px, py, pz, field_rng):
    """Evaluate Gunung Kencana geological domains and grades at XYZ points."""
    zt_p = topo(px, py)
    depth_p = np.maximum(0.0, zt_p - pz)
    d_ox_p, d_tr_p = weathering_depths(px, py)
    dom_p = np.where(depth_p <= d_ox_p, "OXIDE", np.where(depth_p <= d_tr_p, "TRANS", "FRESH"))

    P_loc = np.column_stack([px, py, pz]) - P0
    u_p = P_loc @ s_hat
    v_p = P_loc @ d_hat
    w_p = P_loc @ n_hat

    sw_p = swell_n(u_p, v_p)
    half_w_p = 56.0 + 18.0 * sw_p
    taper_u_p = np.clip(1.0 - np.maximum(0.0, np.abs(u_p) - 165.0) / 85.0, 0.0, 1.0)
    taper_v_p = np.clip(1.0 - np.maximum(0.0, v_p - 85.0) / 60.0, 0.0, 1.0)
    env_p = taper_u_p * taper_v_p

    sh1 = 0.85 * np.exp(-0.5 * (((u_p + 75.0) / 95.0) ** 2 + ((v_p + 10.0) / 70.0) ** 2))
    sh2 = 0.72 * np.exp(-0.5 * (((u_p - 95.0) / 85.0) ** 2 + ((v_p - 25.0) / 65.0) ** 2))
    sh_p = sh1 + sh2

    zf_p = 0.78 * au_3d(px, py, pz) + 0.62 * field_rng.standard_normal(px.size)
    zf_p = np.clip(zf_p, -2.8, 3.0)

    core_p = (env_p > 0.15) & (np.abs(w_p) <= half_w_p * np.sqrt(env_p))
    dout_p = np.maximum(0.0, np.abs(w_p) - half_w_p * np.sqrt(np.maximum(env_p, 1e-6)))
    halo_p = (~core_p) & (env_p > 0.10) & (dout_p <= 32.0)

    log_au_c = -0.15 + 0.68 * sh_p + 0.55 * np.log(np.maximum(env_p, 0.1)) + 0.78 * zf_p
    au_c = np.clip(np.exp(log_au_c), 0.05, 15.0)
    au_h = np.clip(0.55 * env_p * np.exp(-dout_p / 16.0) * np.exp(0.58 * zf_p), 0.01, 4.5)
    au_b = np.clip(0.018 * np.exp(0.55 * field_rng.standard_normal(px.size)), 0.005, 0.08)
    au_p = np.clip(np.where(core_p, au_c, np.where(halo_p, au_h, au_b)), 0.005, 15.0)

    ag_r = 7.5 * np.exp(0.28 * ag_3d(px, py, pz) + 0.22 * field_rng.standard_normal(px.size))
    ag_p = np.where(
        core_p | halo_p,
        au_p * ag_r,
        np.clip(0.12 * np.exp(0.4 * field_rng.standard_normal(px.size)), 0.02, 0.8),
    )
    ag_p = np.clip(ag_p, 0.02, 120.0)

    den_n_p = 0.06 * den_3d(px, py, pz) + 0.03 * field_rng.standard_normal(px.size)
    sg_p = np.select(
        [dom_p == "OXIDE", dom_p == "TRANS"],
        [np.clip(2.15 + den_n_p, 1.92, 2.36), np.clip(2.45 + den_n_p, 2.25, 2.62)],
        default=np.clip(2.68 + den_n_p, 2.52, 2.86),
    )

    alt_p = np.where(
        core_p, "SIL",
        np.where(halo_p | ((env_p > 0.08) & (dout_p <= 45.0)), "ARG", "PROP"),
    )
    return dict(
        domain=dom_p, alt=alt_p, au=au_p, ag=ag_p, sg=sg_p,
        env=env_p, dout=dout_p,
    )


# 50 m infill in mineralized corridor + 100 m flank grid across footprint
dh_nodes = set()
for gx_off in np.arange(200.0, 901.0, 100.0):
    for gy_off in np.arange(200.0, 901.0, 100.0):
        dh_nodes.add((round(gx_off, 1), round(gy_off, 1)))
for gx_off in np.arange(400.0, 701.0, 50.0):
    for gy_off in np.arange(350.0, 701.0, 50.0):
        dh_nodes.add((round(gx_off, 1), round(gy_off, 1)))
dh_nodes = sorted(dh_nodes, key=lambda p: (p[1], p[0]))

rows_col, rows_sur, rows_asy, rows_lit = [], [], [], []
for idx_h, (gx_off, gy_off) in enumerate(dh_nodes, start=1):
    bhid = f"GK-{idx_h:03d}"
    cx_h = float(X0 + gx_off + rng_dh.normal(0.0, 2.5))
    cy_h = float(Y0 + gy_off + rng_dh.normal(0.0, 2.5))
    cx_h = float(np.clip(cx_h, X0 + 180.0, X0 + 960.0))
    cy_h = float(np.clip(cy_h, Y0 + 160.0, Y0 + 960.0))
    cz_h = float(np.round(bilinear_surface_z(tx, ty, gz_t, cx_h, cy_h), 2))

    az0 = float(240.0 + rng_dh.normal(0.0, 4.0))
    dip0 = float(np.clip(62.0 + rng_dh.normal(0.0, 3.5), 55.0, 70.0))
    in_corridor = (380.0 <= (cx_h - X0) <= 720.0) and (330.0 <= (cy_h - Y0) <= 720.0)
    td_target = rng_dh.uniform(175.0, 235.0) if in_corridor else rng_dh.uniform(130.0, 195.0)

    # Cap TD so hole bottom stays strictly inside [X0..X0+1050, Y0..Y0+1050, Z_MIN_C..Z_MAX_C]
    max_td_z = (cz_h - (Z_MIN_C + 5.0)) / np.sin(dip0 * D2R)
    td_h = float(np.round(np.clip(td_target, 120.0, min(240.0, max_td_z)), 1))

    at = np.arange(0.0, td_h, 30.0)
    if at[-1] < td_h - 1.0:
        at = np.append(at, td_h)
    else:
        at[-1] = td_h
    az_walk = np.cumsum(rng_dh.normal(0.0, 0.9, at.size)) * np.sqrt(at / 30.0 + 1.0)
    azs = (az0 + az_walk - az_walk[0]) % 360.0
    dip_walk = np.cumsum(rng_dh.normal(0.0, 0.25, at.size))
    dips = np.clip(dip0 - 0.4 * (at / 30.0) + (dip_walk - dip_walk[0]), 48.0, 78.0)

    # Verify trajectory stays inside block model bounds; trim TD if deviation approaches edge
    probe_d = np.arange(0.0, td_h + 0.1, 2.0)
    if probe_d[-1] < td_h:
        probe_d = np.append(probe_d, td_h)
    probe_p = np.array([cx_h, cy_h, cz_h])[None, :] + desurvey(at, azs, dips, probe_d)
    inside_bm = (
        (probe_p[:, 0] >= X0 + 10.0) & (probe_p[:, 0] <= X0 + NX * DX - 10.0)
        & (probe_p[:, 1] >= Y0 + 10.0) & (probe_p[:, 1] <= Y0 + NY * DY - 10.0)
        & (probe_p[:, 2] >= Z_MIN_C + 2.0) & (probe_p[:, 2] <= Z_MAX_C)
    )
    if not inside_bm.all():
        first_out = int(np.argmax(~inside_bm))
        td_h = float(np.round(max(120.0, probe_d[max(first_out - 1, 0)]), 1))
        at = at[at < td_h - 1.0]
        at = np.append(at, td_h)
        azs = azs[:at.size]
        dips = dips[:at.size]

    rows_col.append((bhid, cx_h, cy_h, cz_h, td_h))
    for a_val, az_val, d_val in zip(at, azs, dips):
        rows_sur.append((bhid, float(a_val), float(az_val), float(d_val)))

    # Determine dense 1 m sampling zone along hole where env_strength > 0.08
    step_d = np.arange(0.25, td_h, 0.5)
    step_p = np.array([cx_h, cy_h, cz_h])[None, :] + desurvey(at, azs, dips, step_d)
    step_eval = eval_emas_field(step_p[:, 0], step_p[:, 1], step_p[:, 2], rng_dh)
    near_min = (step_eval["env"] > 0.08) & (step_eval["dout"] <= 36.0)
    near_d = step_d[near_min]
    lo_d = near_d.min() - 4.0 if near_d.size else -1.0
    hi_d = near_d.max() + 4.0 if near_d.size else -1.0

    ivs, cur = [], 0.0
    while cur < td_h - 0.05:
        ln = 1.0 if (near_d.size and lo_d <= cur <= hi_d) else 2.0
        nxt = min(cur + ln, td_h)
        if nxt - cur < 0.3 and ivs:
            ivs[-1] = (ivs[-1][0], nxt)
        else:
            ivs.append((cur, nxt))
        cur = nxt

    mids = np.array([0.5 * (f_i + t_i) for f_i, t_i in ivs], dtype=float)
    mid_p = np.array([cx_h, cy_h, cz_h])[None, :] + desurvey(at, azs, dips, mids)
    mid_eval = eval_emas_field(mid_p[:, 0], mid_p[:, 1], mid_p[:, 2], rng_dh)
    for j, (f_i, t_i) in enumerate(ivs):
        rows_asy.append((
            bhid, f_i, t_i,
            float(mid_eval["au"][j]), float(mid_eval["ag"][j]), float(mid_eval["sg"][j]),
        ))

    # Lithology & alteration contiguous intervals 0..TD
    edges_lit = np.arange(0.0, td_h, 0.5)
    edges_lit = np.append(edges_lit, td_h)
    mids_lit = 0.5 * (edges_lit[:-1] + edges_lit[1:])
    lit_p = np.array([cx_h, cy_h, cz_h])[None, :] + desurvey(at, azs, dips, mids_lit)
    lit_eval = eval_emas_field(lit_p[:, 0], lit_p[:, 1], lit_p[:, 2], rng_dh)
    doms_l = lit_eval["domain"]
    alts_l = lit_eval["alt"]
    b_idx = 0
    for j in range(1, mids_lit.size + 1):
        end = j == mids_lit.size
        if end or doms_l[j] != doms_l[b_idx] or alts_l[j] != alts_l[b_idx]:
            rows_lit.append((
                bhid, float(edges_lit[b_idx]), float(edges_lit[j]),
                str(doms_l[b_idx]), str(alts_l[b_idx]),
            ))
            b_idx = j

col_df = pd.DataFrame(rows_col, columns=["BHID", "XCOLLAR", "YCOLLAR", "ZCOLLAR", "TD"])
sur_df = pd.DataFrame(rows_sur, columns=["BHID", "AT", "AZ", "DIP"])
asy_df = pd.DataFrame(rows_asy, columns=["BHID", "FROM", "TO", "AU_GPT", "AG_GPT", "SG"])
lit_df = pd.DataFrame(rows_lit, columns=["BHID", "FROM", "TO", "LITH", "ALT"])

for c, nd in dict(XCOLLAR=2, YCOLLAR=2, ZCOLLAR=2, TD=1).items():
    col_df[c] = col_df[c].round(nd)
for c, nd in dict(AT=1, AZ=1, DIP=1).items():
    sur_df[c] = sur_df[c].round(nd)
for c, nd in dict(FROM=2, TO=2, AU_GPT=3, AG_GPT=2, SG=2).items():
    asy_df[c] = asy_df[c].round(nd)
for c in ("FROM", "TO"):
    lit_df[c] = lit_df[c].round(2)

col_df.to_csv(os.path.join(OUT, "collar.csv"), index=False)
sur_df.to_csv(os.path.join(OUT, "survey.csv"), index=False)
asy_df.to_csv(os.path.join(OUT, "assay.csv"), index=False)
lit_df.to_csv(os.path.join(OUT, "litho.csv"), index=False)

dh_ore = asy_df[asy_df["AU_GPT"] >= 0.5]
print(f"Drillholes    : {len(col_df)} holes, {col_df['TD'].sum():.1f} m, survey={len(sur_df)}, assay={len(asy_df)}, litho={len(lit_df)}")
print(f"DH Au>=0.5 g/t: n={len(dh_ore)}, mean={dh_ore['AU_GPT'].mean():.2f}, med={dh_ore['AU_GPT'].median():.2f}, max={dh_ore['AU_GPT'].max():.2f}")
