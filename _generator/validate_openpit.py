"""Validate open-pit block models, topo CSV/DXF parity, drillholes, and spatial coherency."""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import bilinear_surface_z, desurvey

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SETS = [
    ("04-emas-open-pit", 116056, (15, 15, 10), "EPSG:32748",
     {"OXIDE", "TRANS", "FRESH"}, ["AU_GPT", "AG_GPT"],
     ["AU_GPT", "AG_GPT", "SG"], {"OXIDE", "TRANS", "FRESH"}, {"ARG", "SIL", "PROP"}),
    ("05-nikel-laterit-open-pit", 28855, (25, 25, 2), "EPSG:32751",
     {"OVB", "LIM", "SAP", "BRK"},
     ["NI_PCT", "CO_PCT", "FE_PCT", "MGO_PCT", "SIO2_PCT"],
     ["NI_PCT", "CO_PCT", "FE_PCT", "MGO_PCT", "SIO2_PCT", "SG"],
     {"OVB", "LIM", "SAP", "BRK"}, None),
]
fail = 0


def chk(cond, msg):
    global fail
    print(("   OK   " if cond else "  GAGAL ") + msg)
    if not cond:
        fail += 1


def dxf_faces(path):
    """Read ASCII DXF 3DFACE entities and return their layer and vertices."""
    lines = open(path, encoding="ascii").read().splitlines()
    pairs = [(lines[i].strip(), lines[i + 1].strip())
             for i in range(0, len(lines) - 1, 2)]
    faces = []
    for i, (code, value) in enumerate(pairs):
        if code != "0" or value != "3DFACE":
            continue
        fields = dict(pairs[i + 1:i + 14])
        vertices = []
        for xcode, ycode, zcode in (("10", "20", "30"), ("11", "21", "31"),
                                    ("12", "22", "32"), ("13", "23", "33")):
            vertices.append(tuple(float(fields[c]) for c in (xcode, ycode, zcode)))
        faces.append((fields.get("8"), vertices))
    return pairs, faces


def count_overlaps(df):
    """Count overlapping FROM/TO intervals grouped by BHID."""
    ov = 0
    for _, grp in df.sort_values(["BHID", "FROM"]).groupby("BHID"):
        f = grp.FROM.to_numpy()
        t = grp.TO.to_numpy()
        ov += int((f[1:] < t[:-1] - 1e-6).sum())
    return ov


def desurvey_assay_midpoints(col, sur, asy):
    """Return Nx3 array of XYZ midpoints for every assay row."""
    col_map = col.set_index("BHID")
    sur_groups = {b: g.sort_values("AT") for b, g in sur.groupby("BHID")}
    asy_groups = {b: g.sort_values("FROM") for b, g in asy.groupby("BHID")}
    pts = []
    for bhid, a_grp in asy_groups.items():
        if bhid not in col_map.index or bhid not in sur_groups:
            continue
        c_row = col_map.loc[bhid]
        s_grp = sur_groups[bhid]
        mids = 0.5 * (a_grp.FROM.to_numpy() + a_grp.TO.to_numpy())
        off = desurvey(s_grp.AT.to_numpy(), s_grp.AZ.to_numpy(), s_grp.DIP.to_numpy(), mids)
        pts.append(np.array([c_row.XCOLLAR, c_row.YCOLLAR, c_row.ZCOLLAR])[None, :] + off)
    return np.vstack(pts) if pts else np.empty((0, 3), dtype=float)


for folder, expected_rows, dims, crs, domains, grades, dh_asy_cols, lith_codes, alt_codes in SETS:
    path = os.path.join(BASE, folder)
    print("\n" + "=" * 68 + "\n" + folder + "\n" + "=" * 68)
    meta = open(os.path.join(path, "block_model.csv"), encoding="utf-8").readline()
    topo_meta = open(os.path.join(path, "surface_topo.csv"), encoding="utf-8").readline()
    chk(crs in meta and "VERTICAL_DATUM: MSL" in meta,
        "metadata block model menyatakan CRS dan datum vertikal")
    chk(crs in topo_meta and "VERTICAL_DATUM: MSL" in topo_meta,
        "metadata topografi menyatakan CRS dan datum vertikal")
    blocks = pd.read_csv(os.path.join(path, "block_model.csv"), comment="#")
    topo = pd.read_csv(os.path.join(path, "surface_topo.csv"), comment="#")
    chk(len(blocks) == expected_rows, "jumlah blok sesuai (%d)" % expected_rows)
    chk(set(["X", "Y", "Z", "DX", "DY", "DZ", "DENSITY", "DOMAIN", "CLASS"] + grades)
        <= set(blocks.columns), "skema block model lengkap")
    chk(np.isfinite(blocks[["X", "Y", "Z", "DX", "DY", "DZ", "DENSITY"]].to_numpy()).all(),
        "koordinat, dimensi, dan densitas finite")
    chk(all((blocks[c] == size).all() for c, size in zip(("DX", "DY", "DZ"), dims)),
        "ukuran blok sesuai %s m" % " x ".join(map(str, dims)))
    chk(set(blocks.DOMAIN) == domains, "kode domain sesuai: " + ", ".join(sorted(domains)))
    chk(set(blocks.CLASS) <= {"Measured", "Indicated", "Inferred"},
        "kelas berisi nilai yang dikenal")
    chk(np.isfinite(blocks[grades].to_numpy()).all() and (blocks[grades] >= 0).all().all(),
        "kadar finite dan tidak negatif")
    chk(list(topo.columns) == ["X", "Y", "Z"] and np.isfinite(topo.to_numpy()).all(),
        "CSV topografi memiliki X,Y,Z finite")

    xs, ys = np.sort(topo.X.unique()), np.sort(topo.Y.unique())
    xy_pairs = set(zip(topo.X, topo.Y))
    expected_xy = {(x, y) for x in xs for y in ys}
    regular_grid = (
        len(xy_pairs) == len(topo) and xy_pairs == expected_xy
        and np.allclose(np.diff(xs), np.diff(xs)[0])
        and np.allclose(np.diff(ys), np.diff(ys)[0])
    )
    chk(regular_grid, "titik topografi membentuk grid reguler lengkap")
    dxf_pairs, faces = dxf_faces(os.path.join(path, "surface_topo.dxf"))
    expected_faces = 2 * (len(xs) - 1) * (len(ys) - 1)
    chk(len(faces) == expected_faces, "DXF berisi %d segitiga 3DFACE" % expected_faces)
    chk(all(layer == "TOPOGRAPHY" for layer, _ in faces), "semua face berada di layer TOPOGRAPHY")
    csv_points = set(map(tuple, topo[["X", "Y", "Z"]].to_numpy()))
    dxf_points = {point for _, vertices in faces for point in vertices[:3]}
    chk(dxf_points == csv_points, "titik sudut DXF cocok persis dengan surface_topo.csv")
    chk(any(dxf_pairs[i + 1] == ("70", "6")
            for i, pair in enumerate(dxf_pairs[:-1]) if pair == ("9", "$INSUNITS")),
        "DXF menyatakan unit meter (INSUNITS=6)")

    # --- drillhole tables
    dh_files = ("collar.csv", "survey.csv", "assay.csv", "litho.csv")
    chk(all(os.path.isfile(os.path.join(path, name)) for name in dh_files),
        "keempat file drillhole tersedia (collar, survey, assay, litho)")
    chk(all(not open(os.path.join(path, name), encoding="utf-8").readline().startswith("#")
            for name in dh_files),
        "CSV drillhole memakai header polos tanpa baris komentar #")

    col = pd.read_csv(os.path.join(path, "collar.csv"))
    sur = pd.read_csv(os.path.join(path, "survey.csv"))
    asy = pd.read_csv(os.path.join(path, "assay.csv"))
    lit = pd.read_csv(os.path.join(path, "litho.csv"))

    chk(list(col.columns) == ["BHID", "XCOLLAR", "YCOLLAR", "ZCOLLAR", "TD"],
        "skema collar.csv lengkap")
    chk(list(sur.columns) == ["BHID", "AT", "AZ", "DIP"],
        "skema survey.csv lengkap")
    chk(list(asy.columns) == ["BHID", "FROM", "TO"] + dh_asy_cols,
        "skema assay.csv lengkap")
    expected_lit_cols = ["BHID", "FROM", "TO", "LITH"] + (["ALT"] if alt_codes else [])
    chk(list(lit.columns) == expected_lit_cols, "skema litho.csv lengkap")

    chk(len(col) > 0 and col.BHID.is_unique, "BHID collar unik dan tidak kosong")
    chk(set(asy.BHID) <= set(col.BHID), "semua BHID assay ada di collar")
    chk(set(sur.BHID) <= set(col.BHID), "semua BHID survey ada di collar")
    chk(set(lit.BHID) <= set(col.BHID), "semua BHID litho ada di collar")
    chk(set(col.BHID) == set(sur.BHID), "setiap lubang punya survey")

    chk((asy.TO > asy.FROM).all() and (asy.FROM >= -1e-9).all(),
        "assay FROM < TO dan tidak negatif")
    chk((lit.TO > lit.FROM).all() and (lit.FROM >= -1e-9).all(),
        "litho FROM < TO dan tidak negatif")
    asy_ov = count_overlaps(asy)
    lit_ov = count_overlaps(lit)
    chk(asy_ov == 0, "tidak ada interval assay bertumpang tindih (overlap=%d)" % asy_ov)
    chk(lit_ov == 0, "tidak ada interval litho bertumpang tindih (overlap=%d)" % lit_ov)

    td_s = col.set_index("BHID").TD
    asy_over = float((asy.groupby("BHID").TO.max() - td_s).max())
    sur_over = float((sur.groupby("BHID").AT.max() - td_s).max())
    lit_over = float((lit.groupby("BHID").TO.max() - td_s).max())
    chk(asy_over <= 0.051 and sur_over <= 0.051 and lit_over <= 0.051,
        "assay, survey, dan litho tidak melewati TD collar")
    chk(sur.AZ.between(0.0, 360.0).all(), "azimut survey 0-360")
    chk(sur.DIP.between(0.0, 90.0).all(), "dip survey 0-90 (positif ke bawah)")

    chk(np.isfinite(asy[dh_asy_cols].to_numpy()).all() and (asy[dh_asy_cols] >= 0).all().all(),
        "kadar drillhole finite dan tidak negatif")
    chk(set(lit.LITH) <= lith_codes, "kode LITH sesuai: " + ", ".join(sorted(lith_codes)))
    if alt_codes is not None:
        chk(set(lit.ALT) <= alt_codes, "kode ALT sesuai: " + ", ".join(sorted(alt_codes)))

    # --- spatial coherency: collar on surface_topo + midpoints inside block_model
    in_topo_xy = (
        col.XCOLLAR.between(xs.min(), xs.max()).all()
        and col.YCOLLAR.between(ys.min(), ys.max()).all()
    )
    chk(in_topo_xy, "semua collar berada di dalam batas XY surface_topo.csv")
    if regular_grid and in_topo_xy:
        z_grid = topo.pivot(index="X", columns="Y", values="Z").loc[xs, ys].to_numpy()
        z_topo_col = bilinear_surface_z(xs, ys, z_grid, col.XCOLLAR.to_numpy(), col.YCOLLAR.to_numpy())
        max_dz = float(np.abs(col.ZCOLLAR.to_numpy() - z_topo_col).max())
    else:
        max_dz = np.inf
    chk(max_dz <= 0.5, "ZCOLLAR cocok dengan elevasi surface_topo.csv (maks beda %.3f m <= 0.5 m)" % max_dz)

    pts = desurvey_assay_midpoints(col, sur, asy)
    dx, dy, dzb = dims
    in_bm_3d = (
        len(pts) == len(asy)
        and np.all((pts[:, 0] >= blocks.X.min() - dx / 2.0) & (pts[:, 0] <= blocks.X.max() + dx / 2.0))
        and np.all((pts[:, 1] >= blocks.Y.min() - dy / 2.0) & (pts[:, 1] <= blocks.Y.max() + dy / 2.0))
        and np.all((pts[:, 2] >= blocks.Z.min() - dzb / 2.0) & (pts[:, 2] <= blocks.Z.max() + dzb / 2.0))
    )
    chk(in_bm_3d, "seluruh midpoint assay ter-desurvey berada di dalam batas 3D block_model.csv")

    if folder == "04-emas-open-pit":
        bm_ore_mean = float(blocks.loc[blocks.AU_GPT >= 0.5, "AU_GPT"].mean())
        dh_ore_mean = float(asy.loc[asy.AU_GPT >= 0.5, "AU_GPT"].mean())
        ratio = dh_ore_mean / bm_ore_mean
        chk(0.70 <= ratio <= 1.30,
            "rata-rata AU_GPT zona mineralisasi konsisten dengan block model (DH=%.2f vs BM=%.2f)"
            % (dh_ore_mean, bm_ore_mean))
        # Spatial pairing check: blocks nearest to high-grade drillhole midpoints must be enriched vs global BM
        ore_idx = (asy.sort_values(["BHID", "FROM"]).AU_GPT.to_numpy() >= 0.5)
        ore_pts = pts[ore_idx]
        bx = np.sort(blocks.X.unique())
        by = np.sort(blocks.Y.unique())
        bz = np.sort(blocks.Z.unique())
        bm_lookup = blocks.set_index(["X", "Y", "Z"])["AU_GPT"]
        nearest_vals = []
        for px, py, pz in ore_pts[::5]:
            nx = bx[int(np.argmin(np.abs(bx - px)))]
            ny = by[int(np.argmin(np.abs(by - py)))]
            nz = bz[int(np.argmin(np.abs(bz - pz)))]
            if (nx, ny, nz) in bm_lookup.index:
                nearest_vals.append(float(bm_lookup.loc[(nx, ny, nz)]))
        paired_mean = float(np.mean(nearest_vals)) if nearest_vals else 0.0
        chk(paired_mean >= 0.70,
            "koherensi spasial 3D Au teruji: blok terdekat sampel Au>=0.5 bernilai tinggi (mean=%.2f g/t)" % paired_mean)
    else:
        bm_sap_mean = float(blocks.loc[blocks.DOMAIN == "SAP", "NI_PCT"].mean())
        merged = asy.merge(lit, on="BHID", suffixes=("", "_l"))
        merged = merged[(merged.FROM >= merged.FROM_l) & (merged.TO <= merged.TO_l)]
        dh_sap_mean = float(merged.loc[merged.LITH == "SAP", "NI_PCT"].mean())
        ratio = dh_sap_mean / bm_sap_mean
        chk(0.75 <= ratio <= 1.25,
            "rata-rata NI_PCT saprolit konsisten dengan block model (DH=%.2f%% vs BM=%.2f%%)"
            % (dh_sap_mean, bm_sap_mean))
        fe_mgo_r = float(asy.FE_PCT.corr(asy.MGO_PCT))
        chk(fe_mgo_r <= -0.75,
            "korelasi negatif Fe vs MgO terjaga pada assay (r=%.3f)" % fe_mgo_r)

print("\n" + "=" * 68 + "\nPEMERIKSAAN GAGAL:", fail, "\n" + "=" * 68)
raise SystemExit(1 if fail else 0)
