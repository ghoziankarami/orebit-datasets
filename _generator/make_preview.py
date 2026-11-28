"""Preview figures for the five Orebit datasets: 2D PNGs and interactive 3D HTML.

    python _generator/make_preview.py                 # all five datasets
    python _generator/make_preview.py 05-nikel-laterit-open-pit

Needs numpy, pandas, matplotlib and plotly (see requirements-preview.txt).
Output: figures/preview-<dataset>.png and docs/3d/<dataset>.html.
Everything is deterministic: no random numbers are used.
"""
import sys
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, Normalize

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import desurvey  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

# grade: column plotted; log: log colour scale; section: (horizontal axis, slab half-width m,
# vertical exaggeration); cutoff: block cut-off drawn in 3D (open-pit sets only).
DATASETS = {
    "01-emas-epitermal": dict(grade="AU_GPT", unit="g/t", log=True, section=("X", 20, 1)),
    "02-nikel-laterit": dict(grade="NI_PCT", unit="% Ni", log=False, section=("X", 30, 6)),
    "03-timah-placer": dict(grade="SN_KGM3", unit="kg/m3 Sn", log=True, section=("X", 15, 10)),
    "04-emas-open-pit": dict(grade="AU_GPT", unit="g/t", log=True, section=("X", 30, 1), cutoff=0.5),
    "05-nikel-laterit-open-pit": dict(grade="NI_PCT", unit="% Ni", log=False, section=("X", 30, 4), cutoff=1.0),
}
NAVY = "#1E3037"
CMAP = "viridis"


def load(folder, root=ROOT):
    """Read every CSV of one dataset folder; '#' metadata lines are skipped."""
    d = Path(root) / folder
    tables = {}
    for name in ("collar", "survey", "assay", "litho", "block_model", "surface_topo"):
        path = d / f"{name}.csv"
        if path.exists():
            tables[name] = pd.read_csv(path, comment="#")
    return tables


def traces(tables):
    """Hole traces as {BHID: (n,3) XYZ array}, desurveyed to every survey station and TD."""
    col = tables["collar"].set_index("BHID")
    out = {}
    for bh, s in tables["survey"].groupby("BHID"):
        s = s.sort_values("AT")
        td = float(col.loc[bh, "TD"])
        depth = np.unique(np.concatenate([s.AT.to_numpy(), [td]]))
        depth = depth[depth <= max(td, s.AT.max())]
        off = desurvey(s.AT.to_numpy(), s.AZ.to_numpy(), s.DIP.to_numpy(), depth)
        c = col.loc[bh]
        out[bh] = np.column_stack([c.XCOLLAR + off[:, 0], c.YCOLLAR + off[:, 1], c.ZCOLLAR + off[:, 2]])
    return out


def composites(tables):
    """Assay intervals with X, Y, Z of the interval midpoint."""
    col = tables["collar"].set_index("BHID")
    surv = {b: g.sort_values("AT") for b, g in tables["survey"].groupby("BHID")}
    parts = []
    for bh, g in tables["assay"].groupby("BHID"):
        s = surv[bh]
        mid = ((g.FROM + g.TO) / 2.0).to_numpy()
        off = desurvey(s.AT.to_numpy(), s.AZ.to_numpy(), s.DIP.to_numpy(), mid)
        c = col.loc[bh]
        q = g.copy()
        q["X"], q["Y"], q["Z"] = c.XCOLLAR + off[:, 0], c.YCOLLAR + off[:, 1], c.ZCOLLAR + off[:, 2]
        parts.append(q)
    return pd.concat(parts, ignore_index=True)


def norm_for(values, log):
    v = values[np.isfinite(values) & (values > 0)]
    hi = float(np.percentile(v, 99))
    return LogNorm(vmin=max(float(np.percentile(v, 5)), hi / 1000), vmax=hi) if log else Normalize(0, hi)


def pick_slab(comp, grade, axis, half):
    """Centre of the slab (on the axis perpendicular to `axis`) holding most high-grade samples."""
    other = "Y" if axis == "X" else "X"
    hi = comp[comp[grade] >= comp[grade].quantile(0.75)]
    centres = np.round(comp[other].to_numpy() / 5) * 5
    best = max(np.unique(centres), key=lambda c: (np.abs(hi[other] - c) <= half).sum())
    return other, float(best)


def topo_grid(topo):
    p = topo.pivot_table(index="Y", columns="X", values="Z")
    return p.columns.to_numpy(), p.index.to_numpy(), p.to_numpy()


def grid_from_blocks(df, a, b, value):
    p = df.pivot_table(index=b, columns=a, values=value, aggfunc="mean")
    return p.columns.to_numpy(), p.index.to_numpy(), p.to_numpy()


def edges(c):
    """Cell edges from sorted cell centres (uniform spacing)."""
    c = np.asarray(c, float)
    step = np.median(np.diff(c)) if len(c) > 1 else 1.0
    return np.concatenate([c - step / 2, [c[-1] + step / 2]])


def draw_preview(folder, out_dir=ROOT / "figures", root=ROOT):
    cfg = DATASETS[folder]
    g, unit, log = cfg["grade"], cfg["unit"], cfg["log"]
    axis, half, ve = cfg["section"]
    t = load(folder, root)
    tr, comp = traces(t), composites(t)
    comp = comp[np.isfinite(comp[g])]
    norm = norm_for(comp[g].to_numpy(), log)
    has_bm = "block_model" in t
    other, centre = pick_slab(comp, g, axis, half)
    ai = 0 if axis == "X" else 1

    fig, axes = plt.subplots(1, 3 if has_bm else 2, figsize=(18 if has_bm else 12, 5.4), constrained_layout=True,
                             gridspec_kw=dict(width_ratios=[1, 1.7, 1] if has_bm else [1, 1.3]))
    ax_plan, ax_sec = axes[0], axes[1]

    # --- plan view -------------------------------------------------------
    if "surface_topo" in t:
        gx, gy, gz = topo_grid(t["surface_topo"])
        cs = ax_plan.contour(gx, gy, gz, levels=12, colors="#9aa5a8", linewidths=0.6)
        ax_plan.clabel(cs, fmt="%d", fontsize=6)
    for xyz in tr.values():
        ax_plan.plot(xyz[:, 0], xyz[:, 1], color="#555", lw=0.6, zorder=2)
    col = t["collar"]
    ax_plan.scatter(col.XCOLLAR, col.YCOLLAR, s=9, c=NAVY, marker="^", zorder=3, label="collar")
    s = comp.sort_values(g)
    sc = ax_plan.scatter(s.X, s.Y, c=s[g], cmap=CMAP, norm=norm, s=5, zorder=4)
    (ax_plan.axhline if other == "Y" else ax_plan.axvline)(centre, color="crimson", lw=0.8, ls="--")
    ax_plan.set_aspect("equal")
    ax_plan.set_title("Plan view" + (" + topography contours (m)" if "surface_topo" in t else ""), fontsize=10)
    ax_plan.set_xlabel("Easting (m)")
    ax_plan.set_ylabel("Northing (m)")
    ax_plan.ticklabel_format(useOffset=False, style="plain")
    ax_plan.tick_params(labelsize=7)
    ax_plan.legend(loc="upper right", fontsize=7)

    # --- vertical section -------------------------------------------------
    if has_bm:
        bm = t["block_model"]
        slab = bm[np.abs(bm[other] - centre) <= half]
        bx, bz, bv = grid_from_blocks(slab, axis, "Z", g)
        ax_sec.pcolormesh(edges(bx), edges(bz), bv, cmap=CMAP, norm=norm, alpha=0.55, shading="flat")
    for xyz in tr.values():
        if np.abs(xyz[:, 1 - ai] - centre).min() <= half:
            ax_sec.plot(xyz[:, ai], xyz[:, 2], color="#555", lw=0.6, zorder=2)
    ss = s[np.abs(s[other] - centre) <= half]
    ax_sec.scatter(ss[axis], ss.Z, c=ss[g], cmap=CMAP, norm=norm, s=9, zorder=4, edgecolors="none")
    if "surface_topo" in t:
        tp = t["surface_topo"]
        nearest = tp[other].iloc[(tp[other] - centre).abs().argmin()]
        line = tp[tp[other] == nearest].sort_values(axis)
        ax_sec.plot(line[axis], line.Z, color="saddlebrown", lw=1.2, label="topography", zorder=3)
        ax_sec.legend(loc="upper right", fontsize=7)
    ax_sec.set_aspect(ve)
    ax_sec.set_title(f"Section: {other} = {centre:.0f} m ± {half} m (vertical exaggeration {ve}×)", fontsize=10)
    ax_sec.set_xlabel(("Easting" if axis == "X" else "Northing") + " (m)")
    ax_sec.set_ylabel("Elevation (m)")
    ax_sec.ticklabel_format(useOffset=False, style="plain")
    ax_sec.tick_params(labelsize=7)

    # --- bench slice of the block model -----------------------------------
    if has_bm:
        ax_b = axes[2]
        bm = t["block_model"]
        zs = np.sort(bm.Z.unique())
        ore = bm[bm[g] >= cfg["cutoff"]]
        zb = float(ore.Z.median()) if len(ore) else float(zs[len(zs) // 2])
        zb = float(zs[np.abs(zs - zb).argmin()])
        bench = bm[bm.Z == zb]
        bx, by, bv = grid_from_blocks(bench, "X", "Y", g)
        ax_b.pcolormesh(edges(bx), edges(by), bv, cmap=CMAP, norm=norm, shading="flat")
        ax_b.set_aspect("equal")
        ax_b.set_title(f"Block-model bench, Z = {zb:.0f} m ({len(bench):,} blocks)", fontsize=10)
        ax_b.set_xlabel("Easting (m)")
        ax_b.set_ylabel("Northing (m)")
        ax_b.ticklabel_format(useOffset=False, style="plain")
        ax_b.tick_params(labelsize=7)

    cb = fig.colorbar(sc, ax=list(axes), shrink=0.8, pad=0.01)
    cb.set_label(f"{g} ({unit}), {'log' if log else 'linear'} scale", fontsize=8)
    n = len(t["collar"])
    fig.suptitle(f"{folder}  ·  {n} holes · {len(comp):,} assays with {g}  ·  synthetic data", fontsize=11, color=NAVY)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"preview-{folder}.png"
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return path


def figure_3d(folder, root=ROOT, max_blocks=12000):
    """Interactive plotly figure: topography, hole traces, assay samples, blocks above cut-off."""
    import plotly.graph_objects as go

    cfg = DATASETS[folder]
    g, unit, log = cfg["grade"], cfg["unit"], cfg["log"]
    t = load(folder, root)
    tr, comp = traces(t), composites(t)
    comp = comp[np.isfinite(comp[g])]
    norm = norm_for(comp[g].to_numpy(), log)
    cmin, cmax = (np.log10(norm.vmin), np.log10(norm.vmax)) if log else (norm.vmin, norm.vmax)
    color = lambda v: np.log10(np.clip(v, norm.vmin, None)) if log else v  # noqa: E731
    tick = dict(title=f"{g} ({unit})")
    if log:
        ticks = np.arange(np.ceil(cmin), np.floor(cmax) + 1)
        tick.update(tickvals=ticks, ticktext=[f"{10 ** k:g}" for k in ticks])

    fig = go.Figure()
    if "surface_topo" in t:
        gx, gy, gz = topo_grid(t["surface_topo"])
        fig.add_trace(go.Surface(x=gx, y=gy, z=gz, colorscale=[[0, "#c9c2b0"], [1, "#8c7b5a"]], showscale=False,
                                 opacity=0.35, name="topography", hoverinfo="skip"))
    xs, ys, zs = [], [], []
    for xyz in tr.values():
        xs += list(xyz[:, 0]) + [None]
        ys += list(xyz[:, 1]) + [None]
        zs += list(xyz[:, 2]) + [None]
    fig.add_trace(go.Scatter3d(x=xs, y=ys, z=zs, mode="lines", line=dict(color="#444", width=2), name="drillholes", hoverinfo="skip"))
    fig.add_trace(go.Scatter3d(
        x=comp.X, y=comp.Y, z=comp.Z, mode="markers", name="assay samples",
        marker=dict(size=3, color=color(comp[g].to_numpy()), colorscale=CMAP, cmin=cmin, cmax=cmax,
                    colorbar=dict(**tick, len=0.7)),
        text=[f"{b}  {f:g}-{to_:g} m<br>{g} = {v:g}" for b, f, to_, v in zip(comp.BHID, comp.FROM, comp.TO, comp[g])],
        hoverinfo="text"))
    if "block_model" in t:
        bm = t["block_model"]
        ore = bm[bm[g] >= cfg["cutoff"]]
        if len(ore) > max_blocks:  # deterministic thinning: keep the highest grades
            ore = ore.nlargest(max_blocks, g)
        fig.add_trace(go.Scatter3d(
            x=ore.X, y=ore.Y, z=ore.Z, mode="markers", name=f"blocks {g} ≥ {cfg['cutoff']:g}", visible="legendonly",
            marker=dict(size=3.5, symbol="square", opacity=0.45, color=color(ore[g].to_numpy()), colorscale=CMAP, cmin=cmin, cmax=cmax),
            text=[f"block {v:g} {unit}" for v in ore[g]], hoverinfo="text"))
    x_rng, y_rng = np.ptp(comp.X), np.ptp(comp.Y)
    z_rng = max(np.ptp(comp.Z), 1.0)
    ve = {"01": 1.0, "02": 4.0, "03": 6.0, "04": 1.0, "05": 3.0}[folder[:2]]
    m = max(x_rng, y_rng)
    fig.update_layout(
        title=f"{folder}: synthetic data, vertical exaggeration {ve:g}×. Click legend items to toggle.",
        scene=dict(aspectmode="manual", aspectratio=dict(x=x_rng / m, y=y_rng / m, z=ve * z_rng / m),
                   xaxis_title="Easting", yaxis_title="Northing", zaxis_title="Elevation (m)",
                   xaxis=dict(tickformat="d"), yaxis=dict(tickformat="d")),
        margin=dict(l=0, r=0, t=40, b=0), legend=dict(x=0.01, y=0.99))
    return fig


def build_3d(folder, out_dir=ROOT / "docs" / "3d", root=ROOT, max_blocks=12000):
    fig = figure_3d(folder, root, max_blocks)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{folder}.html"
    fig.write_html(path, include_plotlyjs="cdn", full_html=True)
    return path


if __name__ == "__main__":
    for name in sys.argv[1:] or DATASETS:
        print(draw_preview(name))
        print(build_3d(name))
