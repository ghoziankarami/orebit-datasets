"""Validate open-pit block models and parity between their topo CSV and DXF."""
import os
import numpy as np
import pandas as pd

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SETS = [
    ("04-emas-open-pit", 116056, (15, 15, 10), "EPSG:32748",
     {"OXIDE", "TRANS", "FRESH"}, ["AU_GPT", "AG_GPT"]),
    ("05-nikel-laterit-open-pit", 28855, (25, 25, 2), "EPSG:32751",
     {"OVB", "LIM", "SAP", "BRK"},
     ["NI_PCT", "CO_PCT", "FE_PCT", "MGO_PCT", "SIO2_PCT"]),
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


for folder, expected_rows, dims, crs, domains, grades in SETS:
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
    chk(len(xy_pairs) == len(topo) and xy_pairs == expected_xy
        and np.allclose(np.diff(xs), np.diff(xs)[0])
        and np.allclose(np.diff(ys), np.diff(ys)[0]),
        "titik topografi membentuk grid reguler lengkap")
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

print("\n" + "=" * 68 + "\nPEMERIKSAAN GAGAL:", fail, "\n" + "=" * 68)
raise SystemExit(1 if fail else 0)
