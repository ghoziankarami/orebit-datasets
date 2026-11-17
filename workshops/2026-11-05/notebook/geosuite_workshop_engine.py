"""GeoSuite workshop companion: transparent, unchanged E7-parity calculations.
Synthetic training only; interpreted geometry/support are shared inputs.
Run steps in order. Refer to public notebook for scientific limitations.
CC BY 4.0 — Ghozian Karami / Orebit.id.
"""

MODE = "pair"


def configure(mode):
    global MODE
    if mode not in ("pair", "loft"):
        raise ValueError("Use pair or loft")
    MODE = mode


def step_01():
    """Original verified calculation, notebook step 1."""
    global \
        PACKAGE_SHA256, \
        PACKAGE_URL, \
        Path, \
        archive, \
        bundle, \
        candidates, \
        hashlib, \
        json, \
        name, \
        os, \
        payload, \
        response, \
        root, \
        urllib, \
        zipfile
    from pathlib import Path
    import hashlib
    import json
    import urllib.request
    import zipfile
    import os

    PACKAGE_URL = "https://raw.githubusercontent.com/ghoziankarami/orebit-datasets/06b8b3a2efcb963ba446ffc683b2e2552f1a0738/workshops/2026-11-05/GeoSuite_Workshop_Nickel_v2.zip"
    PACKAGE_SHA256 = "a665bcb6-e8d38306-22ac2635-44875551-bf85d96e-ca70639f-c899ee85-551697bb".replace(
        "-", ""
    )
    candidates = [
        Path.cwd(),
        Path.cwd() / "GeoSuite_Workshop_Nickel_v2",
        Path.cwd().parent / "GeoSuite_Workshop_Nickel_v2",
    ]
    root = next((p for p in candidates if (p / "dataset/collar.csv").is_file()), None)
    if root is None:
        archive = Path.cwd() / "GeoSuite_Workshop_Nickel_v2.zip"
        with urllib.request.urlopen(PACKAGE_URL, timeout=60) as response:
            payload = response.read()
        assert (
            hashlib.sha256(payload).hexdigest() == PACKAGE_SHA256
        ), "Package checksum mismatch: stop"
        archive.write_bytes(payload)
        with zipfile.ZipFile(archive) as bundle:
            for name in bundle.namelist():
                assert (
                    (Path.cwd() / name).resolve().is_relative_to(Path.cwd().resolve())
                ), "Unsafe archive path"
            bundle.extractall(Path.cwd())
        root = Path.cwd() / "GeoSuite_Workshop_Nickel_v2"
    os.chdir(root)
    print("Dataset tersedia. Empat CSV diperiksa pada sel berikutnya.")


def step_02():
    """Original verified calculation, notebook step 2."""
    global \
        DATA, \
        Path, \
        REF, \
        RESULTS, \
        ROOT, \
        cdist, \
        expected_counts, \
        expected_hash, \
        hashes, \
        hashlib, \
        math, \
        np, \
        os, \
        pd, \
        plt, \
        raw, \
        relative, \
        solve
    from pathlib import Path
    import math
    import hashlib
    import os
    import numpy as np
    import pandas as pd
    from scipy.linalg import solve
    from scipy.spatial.distance import cdist
    import matplotlib.pyplot as plt

    ROOT = Path.cwd()
    DATA = ROOT / "dataset"
    REF = ROOT / "output"
    RESULTS = ROOT / "hasil-python"
    RESULTS.mkdir(exist_ok=True)
    # MODE is set explicitly by configure(), before the first step.
    assert MODE in ("pair", "loft")
    raw = {
        name: pd.read_csv(DATA / f"{name}.csv")
        for name in ("collar", "survey", "assay", "litho")
    }
    expected_counts = {"collar": 340, "survey": 680, "assay": 8751, "litho": 1344}
    assert {name: len(df) for name, df in raw.items()} == expected_counts
    hashes = json.loads((REF / "input-checksums.json").read_text())
    for relative, expected_hash in hashes.items():
        assert (
            hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected_hash
        ), f"Changed input: {relative}"
    print("Mode:", MODE, "Raw counts:", {k: len(v) for k, v in raw.items()})


def step_03():
    """Original verified calculation, notebook step 3."""
    global assay, collar, df, g, hole, name, ordered
    collar = raw["collar"].set_index("BHID", verify_integrity=True)
    assert all(
        set(df.BHID) <= set(collar.index)
        for name, df in raw.items()
        if name != "collar"
    )
    assert np.isfinite(collar[["XCOLLAR", "YCOLLAR", "ZCOLLAR"]]).all().all()
    for name in ("assay", "litho"):
        df = raw[name]
        assert (df.TO > df.FROM).all() and (df.FROM >= 0).all()
        for hole, g in df.groupby("BHID", sort=False):
            ordered = g.sort_values("FROM")
            assert np.all(
                ordered.FROM.to_numpy()[1:] >= ordered.TO.to_numpy()[:-1] - 1e-9
            ), f"Overlap: {name}/{hole}"
    # These specific teaching data are vertical. For deviated surveys use the
    # GeoSuite measured-survey/minimum-curvature path; do not apply this shortcut.
    assert (
        raw["survey"].DIP == 90
    ).all(), "Notebook vertical specialization cannot process deviated holes"
    assert (raw["survey"].AZ == 0).all()
    assay = raw["assay"].copy()
    assay["X"] = assay.BHID.map(collar.XCOLLAR)
    assay["Y"] = assay.BHID.map(collar.YCOLLAR)
    assay["Z"] = assay.BHID.map(collar.ZCOLLAR) - (assay.FROM + assay.TO) / 2
    print("CRS EPSG:32751; metre; Ni percent. Missing Ni:", assay.NI_PCT.isna().sum())
    print("Raw Ni range:", assay.NI_PCT.min(), assay.NI_PCT.max())


def step_04():
    """Original verified calculation, notebook step 4."""
    global ax, fig, scatter
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].hist(assay.NI_PCT.dropna(), bins=35, color="#087f82")
    ax[0].set(
        xlabel="Ni (%)", ylabel="Raw interval count", title="Raw assay distribution"
    )
    scatter = ax[1].scatter(assay.X, assay.Y, c=assay.NI_PCT, s=3, cmap="viridis")
    ax[1].set(
        xlabel="Easting (m)",
        ylabel="Northing (m)",
        title="Measured midpoint observations",
    )
    fig.colorbar(scatter, ax=ax[1], label="Ni (%)")
    plt.tight_layout()
    plt.show()


def step_05():
    """Original verified calculation, notebook step 5."""
    global \
        ax, \
        body, \
        canonical_mesh_hash, \
        faces, \
        fig, \
        local, \
        mesh, \
        mesh_volume, \
        name, \
        params, \
        reference_volume, \
        solid, \
        tri, \
        ui_reference, \
        vertices
    params = json.loads((REF / "parameters.json").read_text())
    ui_reference = json.loads((REF / MODE / "ui-parity.json").read_text())
    assert ui_reference[
        "ui_source"
    ] == "e7f79300-ef474795-a138f922-6eec494e-58abf903".replace("-", "")
    solid = json.loads((REF / MODE / "interpreted-solid.json").read_text())
    mesh = solid["mesh"]

    def canonical_mesh_hash(body):
        normalized = {
            "v": [[float(x) for x in point] for point in body["v"]],
            "f": [[int(x) for x in face] for face in body["f"]],
        }
        return hashlib.sha256(
            json.dumps(normalized, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

    assert canonical_mesh_hash(mesh) == ui_reference["domains"]["SAP"]["mesh_sha256"]
    print(
        "PASS exact SAP vertices/faces hash vs native Core:", canonical_mesh_hash(mesh)
    )
    for name, body in ui_reference["domains"].items():
        assert canonical_mesh_hash(body["mesh"]) == body["mesh_sha256"]
        print("Same interpreted body:", name, "volume", body["volume_m3"], "m3")
    vertices = np.asarray(mesh["v"], float)
    faces = np.asarray(mesh["f"], int)
    # Local origin prevents cancellation with million-metre projected coordinates.
    local = vertices - vertices[0]
    tri = local[faces]
    mesh_volume = abs(
        np.einsum("ij,ij->i", tri[:, 0], np.cross(tri[:, 1], tri[:, 2])).sum() / 6
    )
    reference_volume = params["expected"][MODE]["domains_m3"]["SAP"]
    assert abs(mesh_volume - reference_volume) < 1e-5
    print("Interpreted SAP whole-mesh volume (not block volume):", mesh_volume, "m³")
    fig = plt.figure(figsize=(9, 6))
    ax = fig.add_subplot(projection="3d")
    ax.plot_trisurf(
        vertices[:, 0] - vertices[0, 0],
        vertices[:, 1] - vertices[0, 1],
        vertices[:, 2],
        triangles=faces,
        alpha=0.35,
        color="#d79d26",
        linewidth=0.05,
    )
    ax.set(
        xlabel="Easting offset (m)",
        ylabel="Northing offset (m)",
        zlabel="RL (m)",
        title=MODE + " — frozen teaching interpretation",
    )
    plt.show()


def step_06():
    """Original verified calculation, notebook step 6."""
    global \
        a, \
        along, \
        anchor, \
        boundary, \
        c, \
        clipped_high, \
        clipped_low, \
        det, \
        eda_table, \
        edge, \
        end, \
        expected_eda, \
        heights, \
        high, \
        hits, \
        hole, \
        horizontal, \
        length2, \
        low, \
        on_boundary, \
        pairs, \
        parent_rows, \
        parents, \
        point, \
        q, \
        ranges, \
        row, \
        side, \
        source, \
        start, \
        t, \
        target, \
        triangle, \
        u, \
        unique, \
        v, \
        w1, \
        w2, \
        z
    # Ray/triangle intersection is independent NumPy math. This training mesh has
    # one continuous vertical intersection per interior hole. Never replace
    # multiple disjoint intervals by a first-top/last-bottom envelope.
    anchor = vertices[0]
    t = local[faces]
    a = t[:, 0, :2]
    u = t[:, 1, :2] - a
    v = t[:, 2, :2] - a
    det = u[:, 0] * v[:, 1] - u[:, 1] * v[:, 0]
    horizontal = np.abs(det) > 1e-10
    side = t[~horizontal, :, :2]
    ranges = {}
    boundary = {}
    for hole, c in collar.iterrows():
        point = np.array([c.XCOLLAR, c.YCOLLAR]) - anchor[:2]
        q = point - a
        w1 = np.zeros(len(t))
        w2 = w1.copy()
        w1[horizontal] = (
            q[horizontal, 0] * v[horizontal, 1] - q[horizontal, 1] * v[horizontal, 0]
        ) / det[horizontal]
        w2[horizontal] = (
            u[horizontal, 0] * q[horizontal, 1] - u[horizontal, 1] * q[horizontal, 0]
        ) / det[horizontal]
        hits = horizontal & (w1 >= -1e-10) & (w2 >= -1e-10) & (w1 + w2 <= 1 + 1e-10)
        heights = (
            t[hits, 0, 2]
            + w1[hits] * (t[hits, 1, 2] - t[hits, 0, 2])
            + w2[hits] * (t[hits, 2, 2] - t[hits, 0, 2])
            + anchor[2]
        )
        heights = np.asarray(sorted(heights))
        unique = []
        for z in heights:
            if not unique or abs(z - unique[-1]) > 1e-7:
                unique.append(z)
        if len(unique) < 2:
            continue
        assert (
            len(unique) == 2
        ), f"Multiple intersections need explicit separate bodies: {hole}"
        on_boundary = False
        for triangle in side:
            pairs = [(triangle[i], triangle[j]) for i, j in ((0, 1), (1, 2), (2, 0))]
            start, end = max(pairs, key=lambda pair: np.linalg.norm(pair[1] - pair[0]))
            edge = end - start
            length2 = edge @ edge
            if length2:
                along = (point - start) @ edge / length2
                if (
                    -1e-12 <= along <= 1 + 1e-12
                    and np.linalg.norm(point - start - along * edge) <= 1e-8
                ):
                    on_boundary = True
                    break
        target = boundary if on_boundary else ranges
        target[hole] = (float(c.ZCOLLAR - max(unique)), float(c.ZCOLLAR - min(unique)))
    print(
        "Interior holes:",
        len(ranges),
        "Boundary holes excluded explicitly:",
        len(boundary),
    )
    if MODE == "pair":
        assert len(ranges) == 302 and len(boundary) == 38
    # Same Assay reviewed-geometry parent EDA scope: unweighted raw parent grades,
    # with clipped physical support reported separately; raw values are unchanged.
    parent_rows = []
    for hole, (low, high) in ranges.items():
        source = assay[assay.BHID == hole]
        for row in source.itertuples():
            clipped_low, clipped_high = max(row.FROM, low), min(row.TO, high)
            if clipped_high - clipped_low > 1e-8:
                parent_rows.append(
                    {
                        "source_row": row.Index,
                        "hole_id": hole,
                        "ni_pct": row.NI_PCT,
                        "support_m": clipped_high - clipped_low,
                        "crossing": row.FROM < low - 1e-8 or row.TO > high + 1e-8,
                    }
                )
    parents = pd.DataFrame(parent_rows)
    expected_eda = params["expected"][MODE]["eda"]
    assert len(parents) == expected_eda["parents"]
    assert int(parents.crossing.sum()) == expected_eda["crossing"]
    assert abs(float(parents.support_m.sum()) - expected_eda["support"]) < 1e-8
    assert params["assay"]["final_cap"].startswith(
        "none"
    ), "Baseline final treatment must match UI: no active cap"
    print(
        "PASS same domain-constrained parent EDA population/support as UI:",
        len(parents),
        "parents;",
        int(parents.crossing.sum()),
        "crossing",
    )
    eda_table = pd.DataFrame(
        [
            {
                "scope": "Raw assay",
                "rows": len(assay),
                "Ni_valid": int(assay.NI_PCT.notna().sum()),
                "Ni_missing": int(assay.NI_PCT.isna().sum()),
                "mean_unweighted_Ni_pct": float(assay.NI_PCT.mean()),
            },
            {
                "scope": "SAP reviewed geometry parents",
                "rows": len(parents),
                "Ni_valid": int(parents.ni_pct.notna().sum()),
                "Ni_missing": int(parents.ni_pct.isna().sum()),
                "mean_unweighted_Ni_pct": float(parents.ni_pct.mean()),
            },
        ]
    )
    print(eda_table.to_string(index=False))
    print(
        "Final active treatment: none. Geometry parent EDA is diagnostic, not per-span grade treatment or an automatic cap decision."
    )


def step_07():
    """Original verified calculation, notebook step 7."""
    global \
        c, \
        composites, \
        end, \
        eps, \
        finite, \
        grade, \
        grade_diff, \
        hi, \
        hole, \
        informed, \
        informed_support, \
        left, \
        lengths, \
        lo, \
        max_grade, \
        physical, \
        ref_composite, \
        right, \
        rows, \
        source, \
        start, \
        support_grade_total, \
        support_total, \
        tolerance, \
        weighted
    rows = []
    support_total = 0.0
    support_grade_total = 0.0
    for hole, (start, end) in ranges.items():
        source = assay[assay.BHID == hole]
        for lo in np.arange(start, end - 1e-8, 2.0):
            hi = min(lo + 2, end)
            lengths = np.maximum(
                0, np.minimum(source.TO, hi) - np.maximum(source.FROM, lo)
            ).to_numpy()
            physical = float(lengths.sum())
            if physical <= 1e-8:
                continue
            informed = np.isfinite(source.NI_PCT.to_numpy())
            informed_support = float(lengths[informed].sum())
            weighted = float(lengths[informed] @ source.NI_PCT.to_numpy()[informed])
            grade = weighted / informed_support if informed_support else np.nan
            c = collar.loc[hole]
            rows.append(
                {
                    "hole_id": hole,
                    "from_m": lo,
                    "to_m": hi,
                    "informed_length": physical,
                    "ni_support_m": informed_support,
                    "ni_pct": grade,
                    "midx": c.XCOLLAR,
                    "midy": c.YCOLLAR,
                    "midz": c.ZCOLLAR - (lo + hi) / 2,
                }
            )
            support_total += physical
            support_grade_total += weighted
    composites = pd.DataFrame(rows)
    ref_composite = pd.read_csv(REF / MODE / "composites-2m.csv")
    assert (
        len(composites)
        == len(ref_composite)
        == params["expected"][MODE]["composites_2m"]
    )
    # Key by hole and deterministic interval order; exports round depths to six
    # decimals, so exact binary equality of printed coordinates is not appropriate.
    left = composites.sort_values(["hole_id", "from_m"]).reset_index(drop=True)
    right = ref_composite.sort_values(["hole_id", "from_m"]).reset_index(drop=True)
    assert (left.hole_id == right.hole_id).all()
    assert np.max(np.abs(left.from_m - right.from_m)) <= 5e-7 + 1e-9
    assert np.max(np.abs(left.to_m - right.to_m)) <= 5e-7 + 1e-9
    assert np.array_equal(np.isnan(left.ni_pct), np.isnan(right.ni_pct))
    # Interval export precision can shift both support endpoints. Conservative
    # length-weighted mean error bound: 4*epsilon*max|grade|/(informed_support-2eps).
    eps = 5e-7
    max_grade = assay.NI_PCT.abs().max()
    tolerance = (
        4 * eps * max_grade / np.maximum(left.ni_support_m - 2 * eps, 1e-9) + 5e-11
    )
    finite = np.isfinite(left.ni_pct)
    grade_diff = np.abs(left.ni_pct - right.ni_pct)
    assert (grade_diff[finite] <= tolerance[finite]).all()
    print(
        "Composites:",
        len(composites),
        "Physical support:",
        support_total,
        "m; missing composite Ni:",
        composites.ni_pct.isna().sum(),
    )
    print(
        "Max composite grade difference vs GeoSuite export:",
        grade_diff.max(),
        "percentage points",
    )
    composites.to_csv(RESULTS / f"{MODE}-composites-python.csv", index=False)


def step_08():
    """Original verified calculation, notebook step 8."""
    global \
        angle, \
        ax, \
        axes, \
        azimuth, \
        bins, \
        counts, \
        delta, \
        difference2, \
        direction, \
        distance, \
        eligible, \
        expected, \
        fig, \
        first, \
        gamma, \
        gammas, \
        geometric_input, \
        grades, \
        h, \
        horizontal, \
        keep, \
        lag, \
        lags, \
        maximum, \
        model, \
        reference, \
        samples, \
        second, \
        separation, \
        summation_tolerance, \
        sums, \
        variograms, \
        vertical, \
        xyz, \
        xyz_computed
    samples = composites.dropna(subset=["ni_pct"]).reset_index(drop=True)
    geometric_input = json.loads(
        (REF / MODE / "geometry-full-precision.json").read_text()
    )
    assert [
        s["hole_id"] for s in geometric_input["samples"]
    ] == samples.hole_id.tolist()
    xyz_computed = samples[["midx", "midy", "midz"]].to_numpy()
    xyz = np.asarray([s["xyz"] for s in geometric_input["samples"]], float)
    assert np.max(np.abs(xyz - xyz_computed)) < 1e-6
    # Match the actual Assay-to-Resource CSV serialization, not raw measurement rounding.
    # Composite grades are calculated independently above; only the derived handoff
    # is written/read with ten decimal places, exactly as in the native workflow.
    grades = np.asarray([float(format(v, ".10f")) for v in samples.ni_pct])
    print(
        "Applied derived CSV handoff grade precision: ten decimal places; raw grades unchanged"
    )
    print(
        "Max geometric round-trip difference (m):", np.max(np.abs(xyz - xyz_computed))
    )
    first, second = np.triu_indices(len(samples), 1)
    delta = xyz[second] - xyz[first]
    horizontal = np.hypot(delta[:, 0], delta[:, 1])
    vertical = np.abs(delta[:, 2])
    difference2 = (grades[second] - grades[first]) ** 2
    model = params["models"][MODE]
    assert (
        model == ui_reference["model"]
    ), "Selected model parameters must match the native UI"

    def gamma(h):
        d = np.asarray(h, float)
        r = d / model["range"]
        partial = model["sill"] - model["nugget"]
        return np.where(
            d <= 0,
            0.0,
            model["nugget"] + partial * np.where(r >= 1, 1.0, 1.5 * r - 0.5 * r**3),
        )

    variograms = {}
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    for direction, ax in zip(["EW", "NS", "vert", "omni"], axes.flat):
        lag = 2 if direction == "vert" else 50
        maximum = 20 if direction == "vert" else 500
        distance = vertical if direction == "vert" else horizontal
        eligible = (distance > 0) & (distance <= maximum)
        if direction == "vert":
            eligible &= horizontal <= 5
        elif direction in ("EW", "NS"):
            angle = np.arctan2(delta[:, 0], delta[:, 1])
            azimuth = np.pi / 2 if direction == "EW" else 0
            separation = np.abs(angle - azimuth) % np.pi
            separation = np.minimum(separation, np.pi - separation)
            eligible &= separation <= np.deg2rad(22.5)
        bins = np.floor(distance / lag).astype(int)
        eligible &= bins < 10
        counts = np.bincount(bins[eligible], minlength=10)
        sums = np.bincount(bins[eligible], weights=difference2[eligible], minlength=10)
        keep = counts >= 5
        lags = (np.arange(10)[keep] + 0.5) * lag
        gammas = sums[keep] / (2 * counts[keep])
        reference = ui_reference["directional"][direction]
        if keep.sum() < 3:
            assert reference["status"] == "refused-insufficient-directional-support"
            print(
                direction,
                ": refused,",
                int(keep.sum()),
                "supported bins;",
                int(counts.sum()),
                "pairs; retain previous applied direction as UI does",
            )
            ax.set_title(direction + " — insufficient directional support")
            variograms[direction] = {"status": "refused"}
        else:
            expected = reference["experimental"]
            assert np.array_equal(lags, expected["lags"]) and np.array_equal(
                counts[keep], expected["pairs"]
            )
            # Different summation orders of the same squared differences; error bound
            # uses observed pair count, floating-point epsilon and maximum squared grade.
            summation_tolerance = (
                100
                * np.finfo(float).eps
                * max(1, float(difference2.max()))
                * int(counts.max())
            )
            assert np.max(np.abs(gammas - expected["gammas"])) <= summation_tolerance
            assert int(counts.sum()) == expected["totalPairs"]
            print(
                direction,
                ": PASS",
                int(counts.sum()),
                "pairs;",
                len(lags),
                "bins; max gamma difference",
                float(np.max(np.abs(gammas - expected["gammas"]))),
            )
            ax.scatter(lags, gammas, label="Python experimental")
            ax.scatter(
                expected["lags"],
                expected["gammas"],
                facecolors="none",
                edgecolors="black",
                label="Native GeoSuite reference",
            )
            h = np.linspace(0, maximum, 150)
            ax.plot(h, gamma(h), label="Same selected final spherical model")
            ax.set_title(direction)
            ax.legend(fontsize=7)
            variograms[direction] = {
                "lags": lags.tolist(),
                "gammas": gammas.tolist(),
                "pairs": counts[keep].tolist(),
                "totalPairs": int(counts.sum()),
            }
        ax.set(xlabel="Lag (m)", ylabel="Semivariance (%²)")
    plt.tight_layout()
    plt.show()
    print("Same selected final model:", model)


def step_09():
    """Original verified calculation, notebook step 9."""
    global \
        actual, \
        block_reference, \
        blocks, \
        calculated, \
        estimate, \
        expected, \
        i, \
        name, \
        radius, \
        search, \
        targets, \
        variance_difference, \
        variance_limit
    # Supplied clipped block support is a disclosed geological input from GeoSuite,
    # NOT independently recreated by this notebook. No grade is read as an input.
    block_reference = pd.read_csv(REF / MODE / "block-model-reference.csv")
    blocks = (
        block_reference[block_reference.SUPPORT_VOLUME_M3 > 0]
        .copy()
        .reset_index(drop=True)
    )
    search = params["search"]
    radius = np.array([search["rSemi"], search["rMaj"], search["rMin"]])
    assert (
        search == ui_reference["search"]
    ), "Every applied search parameter must match UI"
    assert (
        search["azDeg"] == 0
        and search["dipDeg"] == 0
        and search["minNeighbors"] == 2
        and search["maxNeighbors"] == 12
    )
    assert (
        search["maxPerHole"] == 0
        and not search["useOctant"]
        and not search["secondPass"]
    )

    def estimate(target, exclude=None, fixed_neighbors=None):
        delta = xyz - np.asarray(target)
        ellipsoid = np.linalg.norm(delta / radius, axis=1)
        valid = ellipsoid <= 1 + 1e-12
        if exclude is not None:
            valid[exclude] = False
        indices = np.flatnonzero(valid)
        # Select top-k by strict normalized distance. The 1e-10 tie rule belongs
        # only to NN within the selected population; it must not change IDW/OK inputs.
        indices = indices[np.argsort(ellipsoid[indices], kind="stable")[:12]]
        if fixed_neighbors is not None:
            indices = np.asarray(fixed_neighbors, int)
            assert (
                len(indices) >= 2
                and len(indices) <= 12
                and np.all(ellipsoid[indices] <= 1 + 1e-12)
            )
            if exclude is not None:
                assert exclude not in indices
        if len(indices) < 2:
            return [np.nan, np.nan, np.nan, len(indices), np.nan, np.nan]
        points = xyz[indices]
        values = grades[indices]
        dist = np.linalg.norm(points - target, axis=1)
        weights = np.where(dist <= 1e-12, 1e9, 1 / np.maximum(dist, 1e-12) ** 2)
        idw = float(weights @ values / weights.sum())
        n = len(indices)
        A = np.ones((n + 1, n + 1))
        A[-1, -1] = 0
        A[:n, :n] = gamma(cdist(points, points))
        np.fill_diagonal(A[:n, :n], 1e-9)
        rhs = np.r_[gamma(dist), 1.0]
        solution = solve(A, rhs, assume_a="sym")
        ok = max(0.0, float(solution[:n] @ values))
        assert abs(solution[:n].sum() - 1) < 1e-9
        solver_tolerance = max(
            2e-11,
            100
            * np.finfo(float).eps
            * np.linalg.cond(A)
            * max(1, np.abs(solution).max(), np.abs(values).max()),
        )
        nearest = min(
            (
                int(i)
                for i in indices
                if abs(ellipsoid[i] - ellipsoid[indices[0]]) <= 1e-10
            )
        )
        return [
            float(grades[nearest]),
            idw,
            ok,
            n,
            solver_tolerance,
            max(0.0, float(solution @ rhs)),
        ]

    targets = np.asarray(geometric_input["block_centres"], float)
    assert targets.shape == (len(blocks), 3)
    # Display CSV has three decimal places; it must not replace full-precision
    # centre inputs near a search-neighbour tie. This is input equivalence, not
    # parameter tuning to match a result.
    assert np.max(np.abs(targets - blocks[["X", "Y", "Z"]].to_numpy())) <= 0.0005 + 1e-9
    calculated = np.asarray([estimate(target) for target in targets])
    for i, name in enumerate(
        [
            "NN_python",
            "IDW_python",
            "OK_python",
            "neighbors_python",
            "solver_tolerance",
            "variance_python",
        ]
    ):
        blocks[name] = calculated[:, i]
    assert blocks.OK_python.notna().all()
    print("Estimated supported blocks:", len(blocks))
    for name in ["NN", "IDW", "OK"]:
        actual = blocks[name + "_python"].to_numpy().astype(np.float32)
        expected = np.asarray(ui_reference["native_stored_grades"][name], np.float32)
        assert np.array_equal(actual, expected), (
            name + " stored Float32 block grades must match UI exactly"
        )
        blocks[name + "_stored"] = actual.astype(float)
        print(name, "PASS exact stored Float32 parity:", len(actual), "blocks")
    # KRIGE_VAR is exported with six decimals from native Float32 storage.
    variance_difference = np.abs(
        blocks.variance_python.to_numpy() - blocks.KRIGE_VAR.to_numpy()
    )
    variance_limit = (
        5e-7
        + np.abs(np.spacing(blocks.KRIGE_VAR.to_numpy().astype(np.float32))) / 2
        + blocks.solver_tolerance.to_numpy()
    )
    assert np.all(
        variance_difference <= variance_limit
    ), "Kriging variance must match UI within its stated storage/export precision"
    assert np.array_equal(
        blocks.neighbors_python, blocks.N_NEIGHBORS
    ), "Every block must use the same neighbour count as UI"
    print(
        "PASS kriging variance and neighbour counts; maximum variance difference:",
        float(variance_difference.max()),
    )


def step_10():
    """Original verified calculation, notebook step 10."""
    global ax, comparison, error, fig, hi, limit, lo, name, predicted, reference
    comparison = []
    for name in ["NN", "IDW", "OK"]:
        predicted = blocks[name + "_python"].to_numpy()
        reference = blocks[name].to_numpy()
        error = predicted - reference
        # GeoSuite stores grades as Float32 and the CSV prints six decimal places.
        # Bound both representations plus a condition-aware double-precision solve.
        limit = 5e-7 + np.abs(np.spacing(reference.astype(np.float32))) / 2
        if name == "OK":
            limit = limit + blocks.solver_tolerance.to_numpy()
        else:
            limit = limit + 3e-12
        assert np.all(
            np.abs(error) <= limit
        ), f"{name} numerical discrepancy beyond stated precision bound"
        comparison.append(
            {
                "method": name,
                "blocks": len(error),
                "max_abs_percentage_points": float(np.max(np.abs(error))),
                "RMSE_percentage_points": float(np.sqrt(np.mean(error**2))),
                "bias_percentage_points": float(error.mean()),
                "precision_check": "PASS",
                "tolerance_basis": "Float32 half-ULP + six-decimal export half-unit + solver bound",
            }
        )
    comparison = pd.DataFrame(comparison)
    print(comparison.to_string(index=False))
    # No universal percentage tolerance: the bound above follows the actual native
    # storage/export precision. Given mesh, coordinates and clipped block support
    # are shared inputs; this is not an independent geological geometry validation.
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.scatter(blocks.OK, blocks.OK_python, s=5)
    lo = min(blocks.OK.min(), blocks.OK_python.min())
    hi = max(blocks.OK.max(), blocks.OK_python.max())
    ax.plot([lo, hi], [lo, hi], color="black")
    ax.set(
        xlabel="GeoSuite OK export Ni (%)",
        ylabel="Python OK Ni (%)",
        title="Actual block comparison, same supported grid",
    )
    plt.show()


def step_11():
    """Original verified calculation, notebook step 11."""
    global \
        actual, \
        ax, \
        cell_hash, \
        cell_size, \
        column, \
        cv, \
        cv_comparison, \
        dx, \
        dy, \
        expected, \
        fig, \
        grid, \
        i, \
        key, \
        limits, \
        method, \
        metric, \
        native_policy_neighbors, \
        neighbours, \
        order, \
        point, \
        predicted, \
        predictions, \
        reference, \
        seeded_targets, \
        selection, \
        sxx, \
        sxy, \
        syy, \
        tolerance, \
        value

    # Match the documented native baseline: at most12 candidates are selected
    # including the target, then self is dropped (up to11 remaining). This is a
    # matching convention, not a claim that every CV design is equivalent.
    def seeded_targets(n, k=200):
        if n <= k:
            return list(range(n))
        state = 0x9E3779B9
        mask = 0xFFFFFFFF
        values = list(range(n))
        for i in range(k):
            state = (state + 0x6D2B79F5) & mask
            temp = ((state ^ (state >> 15)) * (1 | state)) & mask
            temp = (
                ((temp + (((temp ^ (temp >> 7)) * (61 | temp)) & mask)) & mask) ^ temp
            ) & mask
            random = ((temp ^ (temp >> 14)) & mask) / 4294967296
            j = i + int(random * (n - i))
            values[i], values[j] = values[j], values[i]
        return sorted(values[:k])

    def cell_hash(cx, cy, cz):
        return (
            ((cx * 73856093) & 0xFFFFFFFF)
            ^ ((cy * 19349663) & 0xFFFFFFFF)
            ^ ((cz * 83492791) & 0xFFFFFFFF)
        )

    cell_size = 125
    grid = {}
    for i, point in enumerate(xyz):
        key = cell_hash(*(int(math.floor(v / cell_size)) for v in point))
        grid.setdefault(key, []).append(i)

    def native_policy_neighbors(target_index):
        target = xyz[target_index]
        centre = [int(math.floor(v / cell_size)) for v in target]
        visited = set()
        chosen = []
        for ix in range(-2, 3):
            for iy in range(-2, 3):
                for iz in range(-2, 3):
                    key = cell_hash(centre[0] + ix, centre[1] + iy, centre[2] + iz)
                    if key in visited or key not in grid:
                        continue
                    visited.add(key)
                    for index in grid[key]:
                        dx, dy, dz = xyz[index] - target
                        nd = math.sqrt(
                            (dy / 250) ** 2 + (dx / 250) ** 2 + (dz / 50) ** 2
                        )
                        if nd > 1 or len(chosen) == 12 and nd >= chosen[-1][1]:
                            continue
                        place = len(chosen)
                        while place > 0 and chosen[place - 1][1] > nd:
                            place -= 1
                        chosen.insert(place, (index, nd))
                        if len(chosen) > 12:
                            chosen.pop()
        return [index for index, _ in chosen if index != target_index]

    selection = seeded_targets(len(samples), 200)
    assert (
        selection == ui_reference["cv"]["targets"]
    ), "Same deterministic native LOO targets"
    predictions = []
    for order, i in enumerate(selection):
        neighbours = native_policy_neighbors(i)
        assert (
            neighbours == ui_reference["cv"]["selected_neighbor_indices"][order]
        ), "Same native CV selected population, including distance-tie convention"
        if len(neighbours) < 2:
            continue
        value = estimate(xyz[i], exclude=i, fixed_neighbors=neighbours)
        predictions.append([i, *value])
    cv = np.asarray(predictions)
    actual = grades[cv[:, 0].astype(int)]
    cv_comparison = []
    for method, column in [("NN", 1), ("IDW", 2), ("OK", 3)]:
        predicted = cv[:, column]
        reference = np.asarray(ui_reference["cv"]["results"]["pred" + method], float)
        tolerance = cv[:, 5] if method == "OK" else np.full(len(cv), 3e-12)
        assert np.all(np.abs(predicted - reference) <= tolerance)
        dx = actual - actual.mean()
        dy = predicted - predicted.mean()
        sxx = dx @ dx
        syy = dy @ dy
        sxy = dx @ dy
        metric = {
            "n": len(actual),
            "mae": float(np.mean(np.abs(actual - predicted))),
            "rmse": float(np.sqrt(np.mean((actual - predicted) ** 2))),
            "r2": float(sxy * sxy / (sxx * syy)),
            "slope": float(sxy / sxx),
            "meanAct": float(actual.mean()),
            "meanPred": float(predicted.mean()),
            "bias": float(predicted.mean() - actual.mean()),
        }
        for key, expected in ui_reference["cv"]["metrics"][method.lower()].items():
            assert abs(metric[key] - expected) <= max(
                float(np.max(tolerance)) * 20, 3e-10
            ), (method, key, metric[key], expected)
        cv_comparison.append(
            {
                "method": method,
                "valid_pairs": len(actual),
                "RMSE": metric["rmse"],
                "bias": metric["bias"],
                "source_UI_RMSE": ui_reference["cv"]["metrics"][method.lower()]["rmse"],
                "result": "PASS",
            }
        )
    print(pd.DataFrame(cv_comparison).to_string(index=False))
    print(
        "CV r² follows UI squared Pearson correlation; this is not 1-SSE/SST and not drillhole-held-out validation."
    )
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.scatter(actual, cv[:, 3], s=12, color="#087f82")
    limits = [min(actual.min(), cv[:, 3].min()), max(actual.max(), cv[:, 3].max())]
    ax.plot(limits, limits, color="black")
    ax.set(
        xlabel="Observed Ni (%)",
        ylabel="LOO OK prediction Ni (%)",
        title="Same native LOO targets and neighbourhoods",
    )
    plt.show()


def step_12():
    """Original verified calculation, notebook step 12."""
    global \
        DENSITY, \
        ax, \
        cutoff, \
        fig, \
        final_check, \
        gt, \
        mass, \
        mean_tolerance, \
        metal, \
        metal_tolerance, \
        native_half_ulp, \
        ref_estimate, \
        report, \
        selected, \
        tonnes
    DENSITY = params["grid"]["density_t_m3"]
    tonnes = blocks.SUPPORT_VOLUME_M3.to_numpy() * DENSITY
    gt = []
    for cutoff in params["grade_tonnage"]["cutoffs_percent"]:
        selected = blocks.OK_stored.to_numpy() >= cutoff
        mass = float(tonnes[selected].sum())
        metal = float(tonnes[selected] @ blocks.OK_stored.to_numpy()[selected] / 100)
        gt.append(
            {
                "cutoff_Ni_pct": cutoff,
                "tonnes": mass,
                "mean_Ni_pct": 100 * metal / mass if mass else np.nan,
                "contained_Ni_t": metal,
            }
        )
    gt = pd.DataFrame(gt)
    print(gt.to_string(index=False))
    assert np.all(np.diff(gt.tonnes) <= 1e-6)
    assert np.array_equal(gt.cutoff_Ni_pct, ui_reference["grade_tonnage"]["cutoffs"])
    assert np.allclose(
        gt.tonnes.to_numpy() / 1e6,
        ui_reference["grade_tonnage"]["tons"],
        rtol=0,
        atol=1e-10,
    ), "Every cutoff tonnage must match UI"
    assert np.allclose(
        gt.mean_Ni_pct,
        np.asarray(ui_reference["grade_tonnage"]["meanG"], float),
        rtol=0,
        atol=1e-9,
        equal_nan=True,
    ), "Every cutoff mean grade must match UI"
    assert (
        abs(float(tonnes.sum()) - params["expected"][MODE]["estimated"]["tonnes"])
        < 1e-4
    )
    assert float(blocks.SUPPORT_VOLUME_M3.sum()) <= mesh_volume + 1e-5
    # Reconcile aggregate grade and metal against the native Float32 snapshot,
    # using the tonnage-weighted representation error, not an arbitrary percent.
    native_half_ulp = np.abs(np.spacing(blocks.OK.to_numpy().astype(np.float32))) / 2
    mean_tolerance = float(
        tonnes @ native_half_ulp / tonnes.sum() + blocks.solver_tolerance.max() + 1e-10
    )
    metal_tolerance = float(
        tonnes @ native_half_ulp / 100
        + tonnes.sum() * (blocks.solver_tolerance.max() + 1e-10) / 100
        + 1e-4 * grades.max() / 100
    )
    ref_estimate = params["expected"][MODE]["estimated"]
    assert abs(gt.iloc[0].mean_Ni_pct - ref_estimate["meanGrade"]) <= mean_tolerance
    assert (
        abs(gt.iloc[0].contained_Ni_t - ref_estimate["metalTonnes"]) <= metal_tolerance
    )
    print(
        "Aggregate reconciliation PASS; mean-grade tolerance:",
        mean_tolerance,
        "percentage points; contained-metal tolerance:",
        metal_tolerance,
        "t",
    )
    final_check = pd.DataFrame(
        [
            {
                "metric": "Supported volume (m3)",
                "Python": float(blocks.SUPPORT_VOLUME_M3.sum()),
                "GeoSuite": ref_estimate["volume"],
                "absolute_difference": abs(
                    float(blocks.SUPPORT_VOLUME_M3.sum()) - ref_estimate["volume"]
                ),
                "tolerance": 1e-5,
            },
            {
                "metric": "Final tonnage (t)",
                "Python": float(tonnes.sum()),
                "GeoSuite": ref_estimate["tonnes"],
                "absolute_difference": abs(
                    float(tonnes.sum()) - ref_estimate["tonnes"]
                ),
                "tolerance": 1e-4,
            },
            {
                "metric": "Mean Ni (%)",
                "Python": float(gt.iloc[0].mean_Ni_pct),
                "GeoSuite": ref_estimate["meanGrade"],
                "absolute_difference": abs(
                    float(gt.iloc[0].mean_Ni_pct) - ref_estimate["meanGrade"]
                ),
                "tolerance": mean_tolerance,
            },
            {
                "metric": "Contained Ni (t)",
                "Python": float(gt.iloc[0].contained_Ni_t),
                "GeoSuite": ref_estimate["metalTonnes"],
                "absolute_difference": abs(
                    float(gt.iloc[0].contained_Ni_t) - ref_estimate["metalTonnes"]
                ),
                "tolerance": metal_tolerance,
            },
        ]
    )
    final_check["result"] = np.where(
        final_check.absolute_difference <= final_check.tolerance, "PASS", "FAIL"
    )
    assert (final_check.result == "PASS").all()
    print("FINAL UI / NOTEBOOK CHECK, SAME DOMAIN / SUPPORT / DENSITY / CUTOFF:")
    print(final_check.to_string(index=False))
    print(
        f"Final tonnage: {tonnes.sum():,.2f} t; mode={MODE}; cutoff=0% Ni; density={DENSITY} t/m3"
    )
    final_check.to_csv(RESULTS / f"{MODE}-final-ui-comparison.csv", index=False)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(gt.cutoff_Ni_pct, gt.tonnes / 1e6, marker="o")
    ax.set(
        xlabel="Cutoff Ni (%)",
        ylabel="Supported tonnes (Mt)",
        title="Training grade–tonnage: uniform density assumption",
    )
    plt.show()
    comparison.to_csv(RESULTS / f"{MODE}-comparison.csv", index=False)
    gt.to_csv(RESULTS / f"{MODE}-grade-tonnage.csv", index=False)
    blocks.to_csv(RESULTS / f"{MODE}-block-estimates-python.csv", index=False)
    report = {
        "mode": MODE,
        "raw_counts": expected_counts,
        "mesh_sha256": canonical_mesh_hash(mesh),
        "native_UI_source": ui_reference["ui_source"],
        "mesh_volume_m3": mesh_volume,
        "composites": len(composites),
        "composite_physical_support_m": support_total,
        "estimated_blocks": len(blocks),
        "supported_volume_m3": float(blocks.SUPPORT_VOLUME_M3.sum()),
        "tonnes": float(tonnes.sum()),
        "comparison": comparison.to_dict("records"),
        "CV": cv_comparison,
        "directional": variograms,
        "limits": [
            "synthetic educational data",
            "vertical survey specialization",
            "shared interpreted mesh and clipped block support; not independent geometry validation",
            "not SNI/KCMI/JORC compliance or professional sign-off",
            "native UI baseline convention reproduced; not all UI options replicated",
            "no raw grades modified",
        ],
    }
    (RESULTS / f"{MODE}-run-summary.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    print(json.dumps(report, indent=2))


def plot_eda():
    """Additional actual-data visual explanations; no treatment or grade changes."""
    frame = assay.copy()
    frame["lithology"] = "unmapped"
    for hole, ids in frame.groupby("BHID").groups.items():
        intervals = raw["litho"][raw["litho"].BHID == hole].sort_values("FROM")
        md = ((frame.loc[ids, "FROM"] + frame.loc[ids, "TO"]) / 2).to_numpy()
        for row in intervals.itertuples():
            selected = (md >= row.FROM) & (md < row.TO)
            frame.loc[np.asarray(ids)[selected], "lithology"] = row.LITH
    cols = [
        "NI_PCT",
        "CO_PCT",
        "FE_PCT",
        "MGO_PCT",
        "SIO2_PCT",
        "AL2O3_PCT",
        "CR2O3_PCT",
    ]
    fig, axes = plt.subplots(2, 4, figsize=(13, 6))
    for ax, col in zip(axes.flat, cols + ["SG"]):
        values = pd.to_numeric(frame[col], errors="coerce").dropna()
        ax.hist(values, bins=30, color="#0f766e", alpha=0.85)
        ax.set(
            title=col,
            xlabel="dimensionless SG" if col == "SG" else "%",
            ylabel="Intervals",
        )
    fig.suptitle("Raw distributions: different units and scales; no automatic top-cut")
    fig.tight_layout()
    plt.show()
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, population, title in [
        (axes[0], frame, "All lithologies"),
        (axes[1], frame[frame.lithology == "SAP"], "SAP only"),
    ]:
        corr = population[cols].corr()
        image = ax.imshow(corr, vmin=-1, vmax=1, cmap="RdBu_r")
        ax.set_xticks(range(len(cols)), cols, rotation=60, ha="right", fontsize=8)
        ax.set_yticks(range(len(cols)), cols, fontsize=8)
        for y in range(len(cols)):
            for x in range(len(cols)):
                ax.text(
                    x,
                    y,
                    f"{corr.iloc[y,x]:.2f}",
                    ha="center",
                    va="center",
                    fontsize=7,
                    color="black",
                )
        ax.set_title(title + f" (n={len(population)})")
    fig.colorbar(
        image, ax=axes.ravel().tolist(), label="Pairwise Pearson r", shrink=0.65
    )
    fig.suptitle("Pooled correlations can reflect mixed geological populations")
    fig.subplots_adjust(bottom=0.24, top=0.84, wspace=0.55)
    plt.show()
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    lithologies = sorted(frame.lithology.unique())
    palette = dict(zip(lithologies, plt.get_cmap("tab10").colors))
    for ax, (x, y) in zip(
        axes.flat,
        [
            ("MGO_PCT", "NI_PCT"),
            ("FE_PCT", "CO_PCT"),
            ("SIO2_PCT", "FE_PCT"),
            ("AL2O3_PCT", "CR2O3_PCT"),
        ],
    ):
        for lith in lithologies:
            part = frame[frame.lithology == lith]
            ax.scatter(
                part[x],
                part[y],
                s=3,
                alpha=0.25,
                color=palette[lith],
                label=lith,
                rasterized=True,
            )
        ax.set(xlabel=x + " (%)", ylabel=y + " (%)")
    axes[0, 0].legend(markerscale=3, fontsize=8)
    fig.suptitle(
        "Same raw grades, separated by lithology; correlation is not causation"
    )
    fig.tight_layout()
    plt.show()
    frame.groupby("lithology")[cols].agg(
        ["count", "mean", "median", "std", "min", "max"]
    ).to_csv(RESULTS / "raw-grade-by-lithology.csv")
    frame[cols].corr().to_csv(RESULTS / "raw-grade-correlation.csv")
    print(
        "Element grades Ni/Co/Fe are elemental mass percent; MgO/SiO2/Al2O3/Cr2O3 are oxide mass percent. SG is dimensionless, not measured dry bulk density."
    )
    print(
        "Missing values remain missing. Histograms are unweighted interval diagnostics; final resource means use supported tonnes."
    )


def plot_resource():
    """Explain the actual estimated snapshot and support, without new estimates."""
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    for ax, method in zip(axes, ["NN", "IDW", "OK"]):
        ax.hist(blocks[method + "_stored"], bins=25, color="#0f766e")
        ax.set(
            title=method + " estimated block grades",
            xlabel="Ni (%)",
            ylabel="Supported blocks",
        )
    fig.suptitle(MODE + ": same supported blocks; method smoothing differs")
    fig.tight_layout()
    plt.show()
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    finite = blocks[["OK_stored", "IDW_stored", "NN_stored"]].dropna()
    axes[0].scatter(finite.OK_stored, finite.IDW_stored, s=6, alpha=0.4)
    lo = float(finite.min().min())
    hi = float(finite.max().max())
    axes[0].plot([lo, hi], [lo, hi], "k--", lw=1)
    axes[0].set(
        xlabel="OK Ni (%)",
        ylabel="IDW Ni (%)",
        title="Method comparison, not independent validation",
    )
    axes[1].scatter(blocks.X, blocks.Y, c=blocks.OK_stored, s=12, cmap="viridis")
    axes[1].set(
        xlabel="Easting (m)",
        ylabel="Northing (m)",
        title="Supported block centres: OK Ni (%)",
    )
    axes[1].set_aspect("equal")
    fig.tight_layout()
    plt.show()
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].bar(gt.cutoff_Ni_pct, gt.tonnes / 1e6, width=0.35, color="#0f766e")
    axes[0].set(
        xlabel="Cutoff Ni (%)",
        ylabel="Supported million tonnes",
        title="Inventory above cutoff, not reportable resources",
    )
    axes[1].plot(gt.cutoff_Ni_pct, gt.contained_Ni_t, "o-", color="#d97706")
    axes[1].set(
        xlabel="Cutoff Ni (%)",
        ylabel="Contained Ni (t)",
        title="Metal uses grade / 100 × supported tonnes",
    )
    fig.tight_layout()
    plt.show()
    print(
        "Tonnage: sum of clipped support volume × explicit educational dry density 1.6 t/m³. Do not substitute the SG column."
    )
    print(
        "Pair and loft are different interpretations. Shared mesh/support fixes the comparison scope; CP/geological acceptance remains separate."
    )
