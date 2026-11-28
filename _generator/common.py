"""
common.py - utilitas bersama untuk generator dataset sintetis Orebit.
Hanya butuh numpy + pandas (tanpa scipy).

Berisi:
  SmoothNoise   - medan acak halus (value noise multi-oktaf) untuk memodelkan
                  variasi geologi yang berkorelasi spasial
  desurvey      - desurvey minimum curvature (konvensi DIP positif ke bawah,
                  90 = vertikal ke bawah, sama seperti dataset Babbitt)
"""
import numpy as np

D2R = np.pi / 180.0


# --------------------------------------------------------------------------
# Medan acak halus (value noise). Dipakai untuk ketebalan urat, topografi,
# permukaan bedrock, dan variasi kadar yang berkorelasi spasial.
# --------------------------------------------------------------------------
class SmoothNoise:
    """Value noise multi-oktaf pada 2D atau 3D.

    cell     : ukuran sel oktaf pertama dalam meter (= panjang korelasi kasar)
    octaves  : jumlah oktaf; tiap oktaf setengah ukuran, setengah amplitudo
    """

    def __init__(self, rng, origin, extent, cell, octaves=3, ndim=2):
        self.origin = np.asarray(origin, dtype=float)
        self.ndim = ndim
        self.layers = []
        for o in range(octaves):
            c = cell / (2 ** o)
            shape = tuple(int(e / c) + 4 for e in extent)
            g = rng.normal(0.0, 1.0, shape)
            self.layers.append((c, g, 0.5 ** o))
        # Kalibrasi empiris: interpolasi menurunkan varians, jadi faktor
        # normalisasi diukur langsung dari sampel acak di dalam domain.
        self.norm = 1.0
        probe = [self.origin[k] + rng.uniform(0, extent[k], 20000)
                 for k in range(ndim)]
        self.norm = 1.0 / float(np.std(self(*probe)))

    @staticmethod
    def _smoothstep(t):
        return t * t * (3.0 - 2.0 * t)

    def __call__(self, *coords):
        coords = [np.asarray(c, dtype=float) for c in coords]
        total = np.zeros_like(coords[0], dtype=float)
        for c, g, w in self.layers:
            f = [(coords[k] - self.origin[k]) / c + 1.0 for k in range(self.ndim)]
            i0 = [np.clip(np.floor(f[k]).astype(int), 0, g.shape[k] - 2)
                  for k in range(self.ndim)]
            d = [np.clip(f[k] - i0[k], 0.0, 1.0) for k in range(self.ndim)]
            s = [self._smoothstep(d[k]) for k in range(self.ndim)]
            if self.ndim == 2:
                v00 = g[i0[0], i0[1]]
                v10 = g[i0[0] + 1, i0[1]]
                v01 = g[i0[0], i0[1] + 1]
                v11 = g[i0[0] + 1, i0[1] + 1]
                val = ((v00 * (1 - s[0]) + v10 * s[0]) * (1 - s[1])
                       + (v01 * (1 - s[0]) + v11 * s[0]) * s[1])
            else:
                acc = 0.0
                for a in (0, 1):
                    for b in (0, 1):
                        for cc in (0, 1):
                            wgt = ((s[0] if a else 1 - s[0])
                                   * (s[1] if b else 1 - s[1])
                                   * (s[2] if cc else 1 - s[2]))
                            acc = acc + wgt * g[i0[0] + a, i0[1] + b, i0[2] + cc]
                val = acc
            total = total + w * val
        return total * self.norm


# --------------------------------------------------------------------------
# Desurvey minimum curvature.
# Konvensi: DIP positif ke bawah, 90 = vertikal ke bawah (mengikuti Babbitt).
# Inklinasi dari vertikal I = 90 - DIP.
# Sumbu: X = easting, Y = northing, Z = elevasi (positif ke atas).
# --------------------------------------------------------------------------
def desurvey(at, az, dip, depths):
    """Kembalikan array (n,3) offset XYZ dari collar pada kedalaman `depths`.

    at, az, dip : stasiun survey (kedalaman m, azimut deg, dip deg positif turun)
    depths      : kedalaman yang diminta (m), menaik
    """
    at = np.asarray(at, dtype=float)
    az = np.asarray(az, dtype=float)
    dip = np.asarray(dip, dtype=float)
    depths = np.asarray(depths, dtype=float)

    # Rapatkan menjadi langkah 1 m dengan interpolasi sudut linier,
    # lalu terapkan minimum curvature per langkah.
    dmax = max(depths.max(), at.max())
    fine = np.arange(0.0, dmax + 1.0, 1.0)
    fine = np.unique(np.concatenate([fine, depths, at]))
    fine.sort()

    az_f = np.interp(fine, at, np.unwrap(az * D2R) / D2R)
    dip_f = np.interp(fine, at, dip)

    inc = (90.0 - dip_f) * D2R          # inklinasi dari vertikal
    azr = az_f * D2R

    dmd = np.diff(fine)
    i1, i2 = inc[:-1], inc[1:]
    a1, a2 = azr[:-1], azr[1:]

    cos_beta = (np.cos(i2 - i1)
                - np.sin(i1) * np.sin(i2) * (1.0 - np.cos(a2 - a1)))
    cos_beta = np.clip(cos_beta, -1.0, 1.0)
    beta = np.arccos(cos_beta)
    rf = np.where(beta < 1e-9, 1.0, 2.0 / np.where(beta < 1e-9, 1.0, beta)
                  * np.tan(beta / 2.0))

    de = dmd / 2.0 * (np.sin(i1) * np.sin(a1) + np.sin(i2) * np.sin(a2)) * rf
    dn = dmd / 2.0 * (np.sin(i1) * np.cos(a1) + np.sin(i2) * np.cos(a2)) * rf
    dv = dmd / 2.0 * (np.cos(i1) + np.cos(i2)) * rf   # TVD, positif ke bawah

    e = np.concatenate([[0.0], np.cumsum(de)])
    n = np.concatenate([[0.0], np.cumsum(dn)])
    v = np.concatenate([[0.0], np.cumsum(dv)])

    out = np.empty((depths.size, 3), dtype=float)
    out[:, 0] = np.interp(depths, fine, e)
    out[:, 1] = np.interp(depths, fine, n)
    out[:, 2] = -np.interp(depths, fine, v)   # Z elevasi = turun -> negatif
    return out


def hole_vector(az, dip):
    """Vektor satuan arah lubang (X,Y,Z) untuk azimut/dip tunggal."""
    i = (90.0 - dip) * D2R
    a = az * D2R
    return np.array([np.sin(i) * np.sin(a), np.sin(i) * np.cos(a), -np.cos(i)])


def fmt(df, cols_round):
    """Bulatkan kolom sesuai dict {kolom: desimal} untuk keluaran CSV yang rapi."""
    for c, nd in cols_round.items():
        if c in df.columns:
            df[c] = df[c].round(nd)
    return df


def write_surface_dxf(path, xs, ys, grid_z, layer="TOPOGRAPHY", crs=None, vertical_datum=None):
    """Tulis permukaan grid (len(xs), len(ys)) sebagai segitiga 3DFACE DXF R12 ASCII murni.

    Hanya memakai pustaka standar Python + NumPy (tanpa ezdxf) dan dapat dibaca
    langsung oleh ezdxf, Surpac, Datamine, Micromine, Leapfrog, maupun PitOpt.
    """
    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(ys, dtype=float)
    grid_z = np.asarray(grid_z, dtype=float)
    if grid_z.shape != (xs.size, ys.size):
        raise ValueError(f"grid_z shape {grid_z.shape} != ({xs.size}, {ys.size})")

    finite = np.isfinite(grid_z)
    zmin = float(np.min(grid_z[finite])) if finite.any() else 0.0
    zmax = float(np.max(grid_z[finite])) if finite.any() else 0.0

    comment_parts = ["Orebit Synthetic Topography Surface"]
    if crs:
        comment_parts.append(f"CRS: {crs}")
    if vertical_datum:
        comment_parts.append(f"VERTICAL_DATUM: {vertical_datum}")

    lines = [
        "  999",
        " | ".join(comment_parts),
        "  0", "SECTION",
        "  2", "HEADER",
        "  9", "$ACADVER", "  1", "AC1009",
        "  9", "$INSUNITS", " 70", "6",
        "  9", "$EXTMIN", " 10", f"{xs.min():.3f}", " 20", f"{ys.min():.3f}", " 30", f"{zmin:.3f}",
        "  9", "$EXTMAX", " 10", f"{xs.max():.3f}", " 20", f"{ys.max():.3f}", " 30", f"{zmax:.3f}",
        "  0", "ENDSEC",
        "  0", "SECTION",
        "  2", "ENTITIES",
    ]

    faces = 0
    for i in range(xs.size - 1):
        x0, x1 = xs[i], xs[i + 1]
        for j in range(ys.size - 1):
            y0, y1 = ys[j], ys[j + 1]
            z00, z10, z11, z01 = grid_z[i, j], grid_z[i + 1, j], grid_z[i + 1, j + 1], grid_z[i, j + 1]
            if not (np.isfinite(z00) and np.isfinite(z10) and np.isfinite(z11) and np.isfinite(z01)):
                continue
            for p0, p1, p2 in (
                ((x0, y0, z00), (x1, y0, z10), (x1, y1, z11)),
                ((x0, y0, z00), (x1, y1, z11), (x0, y1, z01)),
            ):
                lines.extend([
                    "  0", "3DFACE",
                    "  8", str(layer),
                    " 10", f"{p0[0]:.3f}", " 20", f"{p0[1]:.3f}", " 30", f"{p0[2]:.3f}",
                    " 11", f"{p1[0]:.3f}", " 21", f"{p1[1]:.3f}", " 31", f"{p1[2]:.3f}",
                    " 12", f"{p2[0]:.3f}", " 22", f"{p2[1]:.3f}", " 32", f"{p2[2]:.3f}",
                    " 13", f"{p2[0]:.3f}", " 23", f"{p2[1]:.3f}", " 33", f"{p2[2]:.3f}",
                ])
                faces += 1

    lines.extend(["  0", "ENDSEC", "  0", "EOF", ""])
    with open(path, "w", encoding="ascii", newline="\n") as fh:
        fh.write("\n".join(lines))
    return faces


def write_surface_csv(path, xs, ys, grid_z, crs=None, vertical_datum=None):
    """Tulis grid permukaan ke CSV X,Y,Z dengan header komentar CRS opsional."""
    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(ys, dtype=float)
    grid_z = np.asarray(grid_z, dtype=float)
    mx, my = np.meshgrid(xs, ys, indexing="ij")
    mask = np.isfinite(grid_z)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        if crs or vertical_datum:
            meta = []
            if crs:
                meta.append(f"CRS: {crs}")
            if vertical_datum:
                meta.append(f"VERTICAL_DATUM: {vertical_datum}")
            fh.write("# " + " | ".join(meta) + "\n")
        fh.write("X,Y,Z\n")
        for x, y, z in zip(mx[mask], my[mask], grid_z[mask]):
            fh.write(f"{x:.3f},{y:.3f},{z:.3f}\n")


def bilinear_surface_z(grid_xs, grid_ys, grid_z, xq, yq):
    """Interpolasi bilinear elevasi Z pada grid reguler (grid_xs, grid_ys, grid_z)."""
    grid_xs = np.asarray(grid_xs, dtype=float)
    grid_ys = np.asarray(grid_ys, dtype=float)
    grid_z = np.asarray(grid_z, dtype=float)
    xq_arr = np.asarray(xq, dtype=float)
    yq_arr = np.asarray(yq, dtype=float)
    ix = np.clip(np.searchsorted(grid_xs, xq_arr, side="right") - 1, 0, grid_xs.size - 2)
    iy = np.clip(np.searchsorted(grid_ys, yq_arr, side="right") - 1, 0, grid_ys.size - 2)
    fx = (xq_arr - grid_xs[ix]) / (grid_xs[ix + 1] - grid_xs[ix])
    fy = (yq_arr - grid_ys[iy]) / (grid_ys[iy + 1] - grid_ys[iy])
    vals = (
        (grid_z[ix, iy] * (1.0 - fx) + grid_z[ix + 1, iy] * fx) * (1.0 - fy)
        + (grid_z[ix, iy + 1] * (1.0 - fx) + grid_z[ix + 1, iy + 1] * fx) * fy
    )
    return float(vals) if np.ndim(xq) == 0 and np.ndim(yq) == 0 else vals
