"""Composite attribute values by position: Study 13b's two random studies (Gegenpress, Catenaccio) and Purity's
FM Arena test (3-4-2-1), pooled with a random-effects model.

Unit: goal difference per season for +1 level in ONE player. Groups: ST; AM (AML/AMR, AMC, Purity's AM); FB/WB (DL/DR,
WBL/WBR, Purity's WB); DM; CB; GK. The setups differ beyond noise in proportion to the effect (a tactic scales an
attribute up or down), so each source's value is mean + setup deviation (sd r·|mean|) + sampling noise; r is set so the
heterogeneity statistic equals its degrees of freedom. Checked by predicting each source from the other two.

Purity's tables (published on FM Arena) live in the git-ignored private/: purity_goal_difference.tsv (outfield, all
50 attributes; 95% margins by group from the post) and purity_goalkeeper.tsv (the 13 goalkeeper rows they listed).

    .venv/bin/python port/validation/composite_values.py [runs/composite]
"""
import json, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / p) for p in ('port/validation', 'scripts', 'src')]
GROUPS = ['ST', 'AM', 'FB/WB', 'DM', 'CB', 'GK']
OURS = {'GK': 'GK', 'FB': 'FB/WB', 'CB': 'CB', 'DM': 'DM', 'AM': 'AM', 'ST': 'ST'}
PURITY_GROUP = {'ST': 'ST', 'AM': 'AM', 'WB': 'FB/WB', 'CB': 'CB', 'DM': 'DM'}
PURITY_M95 = {'ST': .09, 'AM': .06, 'WB': .06, 'CB': .05, 'DM': .06}


def ours(style):
    """{(group, attribute): (GD per season, se)} and the per-game win/GD coefficients for the conversion."""
    import random_study as rs
    d = ROOT / 'runs/random' / style; a = json.loads((d / 'analysis.json').read_text())
    gd = a['measures']['GD']; cols = [tuple(c) for c in a['cols']]
    out = {(OURS[g], f): (38 * gd['b'][i], 38 * gd['se'][i]) for i, (g, f) in enumerate(cols)}
    meta = json.loads((d / 'meta.json').read_text()); z = np.load(d / 'design.npz'); X, S = z['X'].astype(float), z['setting']
    win = {}
    for line in open(d / 'results.jsonl'):
        r = json.loads(line); _, c, k = r['cond'].split('|'); me = meta['settings'][int(k)]['venue']
        win[int(c)] = float(r['score'][me] > r['score'][1 - me])
    idx = np.array(sorted(win)); X, S = X[idx], S[idx]; y = np.array([win[c] for c in idx])
    groups = [x['group'] for x in meta['xi']]; F = meta['fields']
    Z = np.stack([X[:, [j for j, gg in enumerate(groups) if gg == g], F.index(f)].sum(1) for g, f in cols], 1)
    wb, wse, _ = rs.regress(y, Z, S, len(meta['settings']))
    w = 1 / (np.array(gd['se']) ** 2); g = np.array(gd['b'])
    k = float((w * g * wb).sum() / (w * g * g).sum())   # win probability per goal of goal difference (per game)
    return out, k, float(y.mean())


def purity():
    out = {}
    lines = (ROOT / 'private/purity_goal_difference.tsv').read_text().strip().split('\n'); hdr = lines[0].split('\t')
    for line in lines[1:]:
        p = line.split('\t'); name = p[0].replace('†', '').strip()
        for h, v in zip(hdr[1:], p[1:]):
            if h in PURITY_GROUP: out[(PURITY_GROUP[h], name)] = (float(v.replace('*', '').replace('+', '')), PURITY_M95[h] / 1.96)
    for line in (ROOT / 'private/purity_goalkeeper.tsv').read_text().strip().split('\n')[1:]:
        name, v, m = line.split('\t'); out[('GK', name)] = (float(v), float(m) / 1.96)
    return out


def pool(ys, ss, r):
    """Random-effects mean with setup sd r·|mean| (iterated), its se, and Q at that r."""
    w = 1 / ss ** 2; m = (w * ys).sum() / w.sum()
    for _ in range(50):
        w = 1 / (ss ** 2 + (r * m) ** 2); m = (w * ys).sum() / w.sum()
    return m, 1 / np.sqrt(w.sum()), float((w * (ys - m) ** 2).sum())


def fit_r(cells):
    lo, hi = 0.0, 3.0
    df = sum(len(y) - 1 for y, _ in cells)
    for _ in range(60):
        r = (lo + hi) / 2; Q = sum(pool(y, s, r)[2] for y, s in cells)
        lo, hi = (r, hi) if Q > df else (lo, r)
    return r, df


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / 'runs/composite'); out.mkdir(parents=True, exist_ok=True)
    (G, kG, wG), (C, kC, wC) = ours('gegenpress'), ours('catenaccio')
    src = {'Gegenpress': G, 'Catenaccio': C, 'Purity': purity()}
    keys = sorted(set(G) | set(C))
    cells = {k: [(n, *src[n][k]) for n in src if k in src[n]] for k in keys}
    multi = [(np.array([c[1] for c in v]), np.array([c[2] for c in v])) for k, v in cells.items() if len(v) > 1 and k[0] != 'GK']
    Q0 = sum(pool(y, s, 0)[2] for y, s in multi); r, df = fit_r(multi)
    k_win = (kG + kC) / 2   # win probability per goal of GD per game; the two styles' values are reported
    res = {}
    for k, v in cells.items():
        y = np.array([c[1] for c in v]); s = np.array([c[2] for c in v]); m, se, _ = pool(y, s, r)
        res[k] = {'gd': m, 'se': se, 't': m / se, 'win6': 6 * 100 * k_win * m / 38, 'win6_se': 6 * 100 * k_win * se / 38,
                  'sources': {c[0]: [c[1], c[2]] for c in v}}
    # check: predict each source from the other two (outfield cells with all three)
    check = {}
    for n in src:
        z = []
        for k, v in cells.items():
            if k[0] == 'GK' or len(v) < 3: continue
            o = [c for c in v if c[0] != n]; t = [c for c in v if c[0] == n][0]
            m, se, _ = pool(np.array([c[1] for c in o]), np.array([c[2] for c in o]), r)
            z.append((t[1] - m) / np.sqrt(se ** 2 + t[2] ** 2 + (r * m) ** 2))
        z = np.array(z); check[n] = {'n': len(z), 'chi2': float((z ** 2).sum()), 'big_z': int((np.abs(z) > 3).sum())}
    meta = {'r': r, 'Q_fixed': Q0, 'df': df, 'k_win': {'Gegenpress': kG, 'Catenaccio': kC, 'used': k_win},
            'base_win': {'Gegenpress': wG, 'Catenaccio': wC}, 'check': check}
    (out / 'composite.json').write_text(json.dumps({'meta': meta, 'cells': [[g, f, v] for (g, f), v in res.items()]}))
    L = ['# Composite attribute values by position', '',
         f"Setups differ beyond noise: Q {Q0:.0f} on {df} df with one common value; spread between setups "
         f"{100 * r:.0f}% of the effect. Win rate per goal of GD per game: Gegenpress {kG:.3f}, Catenaccio {kC:.3f}.", '',
         'Leave-one-source-out: ' + '; '.join(f"{n} chi-square {c['chi2']:.0f} on {c['n']}, |z|>3: {c['big_z']}" for n, c in check.items()), '']
    for g in GROUPS:
        L += [f'## {g}', '', '| Attribute | GD/season | se | t | win % (+6) | sources |', '|---|---|---|---|---|---|']
        for (gg, f), v in sorted(res.items(), key=lambda kv: -kv[1]['gd']):
            if gg != g or (abs(v['t']) < 2 and len(L) > 0 and abs(v['gd']) < 0.05): continue
            L.append(f"| {f} | {v['gd']:+.2f} | {v['se']:.2f} | {v['t']:.1f} | {v['win6']:+.1f} | " +
                     ', '.join(f'{n[0]} {a:+.2f}' for n, (a, _) in v['sources'].items()) + ' |')
        L.append('')
    (out / 'report.md').write_text('\n'.join(L))
    print('\n'.join(L[:6]))


if __name__ == '__main__':
    main()
