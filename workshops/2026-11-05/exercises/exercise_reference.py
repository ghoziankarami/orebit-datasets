"""Independent numerical teaching references, synthetic data only.

CC BY 4.0 — Ghozian Karami / Orebit.id. This does not import GeoSuite code.
Run with Python 3.12, NumPy, SciPy, pandas and matplotlib from the workshop pins.
"""
from pathlib import Path
import json
import math
import numpy as np
import pandas as pd
from scipy.integrate import quad
import matplotlib.pyplot as plt

def direction(azimuth, dip):
    az = math.radians(azimuth)
    dip = math.radians(dip)
    return np.array([math.cos(dip) * math.sin(az), math.cos(dip) * math.cos(az), -math.sin(dip)])

def point_at_md(collar, stations, md):
    """Integrate the rotating tangent numerically, independently of the UI solver."""
    if md < 0 or md > float(stations.AT.max()):
        raise ValueError('Measured depth outside measured station support')
    point = np.array([collar.XCOLLAR, collar.YCOLLAR, collar.ZCOLLAR], float)
    ordered = list(stations.sort_values('AT').itertuples())
    for a, b in zip(ordered[:-1], ordered[1:]):
        if md <= a.AT:
            break
        fraction = min(1, (md - a.AT) / (b.AT - a.AT))
        u, v = (direction(a.AZ, a.DIP), direction(b.AZ, b.DIP))
        angle = math.atan2(float(np.linalg.norm(np.cross(u, v))), float(np.dot(u, v)))
        if math.pi - angle < 1e-06:
            raise ValueError('Opposite directions need measurement review')
        for axis in range(3):

            def tangent(t):
                if angle < 1e-12:
                    return u[axis]
                return (math.sin((1 - t) * angle) * u[axis] + math.sin(t * angle) * v[axis]) / math.sin(angle)
            point[axis] += (b.AT - a.AT) * quad(tangent, 0, fraction, epsabs=1e-12, epsrel=1e-12)[0]
        if fraction < 1:
            break
    return point

def survey_reference(folder):
    folder = Path(folder)
    collar = pd.read_csv(folder / 'collar.csv')
    surveys = pd.read_csv(folder / 'survey.csv')
    assay = pd.read_csv(folder / 'assay.csv')
    rows = []
    for c in collar.itertuples():
        s = surveys[surveys.BHID == c.BHID]
        a = assay[assay.BHID == c.BHID]
        depths = sorted(set(s.AT.tolist() + ((a.FROM + a.TO) / 2).tolist()))
        for md in depths:
            x, y, z = point_at_md(c, s, md)
            rows.append({'BHID': c.BHID, 'MD': md, 'X': x, 'Y': y, 'Z': z, 'TVD': c.ZCOLLAR - z})
    result = pd.DataFrame(rows)
    expected = Path(__file__).parent / 'reference-results/survey-expected-coordinates.csv'
    if expected.exists():
        reference = pd.read_csv(expected)
        assert result.BHID.tolist() == reference.BHID.tolist()
        assert np.max(np.abs(result[['X', 'Y', 'Z']].to_numpy() - reference[['X', 'Y', 'Z']].to_numpy())) < 1e-07
    return result

def qaqc_reference(folder):
    folder = Path(folder)
    data = pd.read_csv(folder / 'qaqc-ni.csv')
    certificate = json.loads((Path(__file__).parent / 'reference-results/qaqc-mock-certificate-and-expected.json').read_text())
    assert certificate['synthetic_only'] and certificate['mock_certificate_not_real_CRM']
    crm = data[data.hole_id.str.startswith('CRM-')].copy()
    crm['z'] = (crm.ni_pct - certificate['mean']) / certificate['sd']
    blanks = data[data.hole_id.str.startswith('BLANK-')].copy()
    blanks['ratio_to_teaching_DL'] = blanks.ni_pct / certificate['declared_teaching_DL']
    paired = []
    for row in data[data.hole_id.str.endswith('-DUP')].itertuples():
        original = float(data[data.hole_id == row.hole_id.removesuffix('-DUP')].ni_pct.iloc[0])
        paired.append({'original': original, 'duplicate': row.ni_pct, 'HARD': abs(original - row.ni_pct) / (original + row.ni_pct) * 100})
    return (crm, blanks, pd.DataFrame(paired))

def plot_survey(folder, output):
    folder = Path(folder)
    output = Path(output)
    output.mkdir(exist_ok=True, parents=True)
    collars = pd.read_csv(folder / 'collar.csv')
    surveys = pd.read_csv(folder / 'survey.csv')
    plt.rcParams.update({'font.size': 14})
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for c in collars.itertuples():
        stations = surveys[surveys.BHID == c.BHID]
        md = np.linspace(0, float(stations.AT.max()), 120)
        points = np.array([point_at_md(c, stations, float(d)) for d in md])
        axes[0].plot(points[:, 0] - c.XCOLLAR, points[:, 2], label=c.BHID)
        axes[1].plot(md, md - (c.ZCOLLAR - points[:, 2]), label=c.BHID)
    axes[0].set(xlabel='Easting displacement (m)', ylabel='Elevation / RL (m)', title='Curved measured-survey scenario')
    axes[1].set(xlabel='Measured depth (m)', ylabel='MD minus TVD (m)', title='Measured length differs from vertical depth')
    axes[0].legend(fontsize=10)
    fig.tight_layout()
    fig.savefig(output / 'survey-curvature.png', dpi=160)
    plt.close(fig)

def plot_qaqc(folder, output):
    output = Path(output)
    output.mkdir(exist_ok=True, parents=True)
    crm, blanks, pairs = qaqc_reference(folder)
    plt.rcParams.update({'font.size': 14})
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))
    axes[0].plot(range(1, len(crm) + 1), crm.z, 'o-')
    for threshold in [-3, 3]:
        axes[0].axhline(threshold, color='#dc2626', ls='--')
    axes[0].set(xlabel='SIMNI control sequence', ylabel='Z score', title='Mock CRM: last control fails')
    axes[1].bar(['BLANK-01', 'BLANK-02'], blanks.ratio_to_teaching_DL, color=['#0f766e', '#dc2626'])
    axes[1].axhline(5, color='#dc2626', ls='--')
    axes[1].set(ylabel='Result / 0.01% Ni', title='Blank teaching threshold')
    axes[1].tick_params(axis='x', labelsize=10)
    axes[2].bar(['CTRL01', 'CTRL02', 'CTRL03'], pairs.HARD, color=['#0f766e', '#dc2626', '#0f766e'])
    axes[2].axhline(20, color='#dc2626', ls='--')
    axes[2].set(ylabel='HARD (%)', title='Duplicate precision')
    axes[2].tick_params(axis='x', labelsize=10)
    fig.tight_layout()
    fig.savefig(output / 'qaqc-mock-results.png', dpi=160)
    plt.close(fig)
if __name__ == '__main__':
    root = Path(__file__).parent
    data_root = root if (root / 'deviated-survey').exists() else root.parents[1] / 'dataset/exercises'
    out = root / 'calculated-output'
    out.mkdir(exist_ok=True)
    survey_reference(data_root / 'deviated-survey').to_csv(out / 'survey-reference.csv', index=False)
    plot_survey(data_root / 'deviated-survey', out)
    plot_qaqc(data_root / 'qaqc-synthetic', out)
    print('Independent synthetic survey and mock QAQC references calculated; not professional validation.')
