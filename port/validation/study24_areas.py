"""Study 24's analysis: which tactical familiarity area is worth training, per style, and whether the styles agree.

  python port/validation/study24_areas.py runs/study24    # writes OUT/areas.md

Per style and area: the paired effect of the area at 80 and at 20 (against all areas at 50) on xPts, xG for, xG
against and xG difference; the swing (80 minus 20, paired on the same matches); the areas ranked by the swing; a test
that the eight areas are equal within a style (chi-square, 7 df) and that the two styles agree (chi-square on the
eight differences, 8 df, and the rank correlation).
"""
import argparse, json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'port/validation')); sys.path.insert(0, str(ROOT / 'src'))
import neutral_study as ns
from random_study import chi2_sf

AREAS = ['In-possession shape', 'Passing style', 'Build-up', 'Chance creation', 'Out-of-possession shape',
         'Line of engagement', 'Pressing intensity', 'Pressing trap']
MEASURES = ('xPts', 'xGF', 'xGA', 'xGD', 'pts')


def paired(data, g, a, b, m):
    """mean, t, se, n of a - b over the matches both have (b may be 'none')."""
    da, db = data.get((g, a), {}), data.get((g, b), {})
    return ns.stat([da[k][m] - db[k][m] for k in da if k in db])


def spearman(x, y):
    rk = lambda v: [sorted(v).index(e) for e in v]
    a, b = rk(x), rk(y); n = len(a); ma, mb = sum(a) / n, sum(b) / n
    return sum((p - ma) * (q - mb) for p, q in zip(a, b)) / math.sqrt(sum((p - ma) ** 2 for p in a) * sum((q - mb) ** 2 for q in b))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('out')
    a = p.parse_args(); out = Path(a.out); meta = json.loads((out / 'meta.json').read_text()); data = ns.load(out)
    styles = [g['name'] for g in meta['groups']]
    f = lambda e: f'{e[0]:+.3f} ({e[1]:+.1f})'
    L = [f"# {meta['title']}: areas", '', 'Per game against every area at 50 (paired); t in brackets. Swing = area at 80 minus the same area at 20.', '']
    swing = {}
    for s in styles:
        base = list(data.get((s, 'none'), {}).values())
        L += [f'## {s}', '', f"Unchanged: {len(base)} matches, xPts {sum(r['xPts'] for r in base) / len(base):.2f}, "
              f"xG {sum(r['xGF'] for r in base) / len(base):.2f} for, {sum(r['xGA'] for r in base) / len(base):.2f} against.", '',
              '| Area | At 80: xPts | xG for | xG against | At 20: xPts | xG for | xG against | Swing: xPts | Swing: xG difference | Pairs |',
              '|---|---|---|---|---|---|---|---|---|---|']
        for ar in AREAS:
            hi = {m: paired(data, s, f'{ar} 80', 'none', m) for m in MEASURES}
            lo = {m: paired(data, s, f'{ar} 20', 'none', m) for m in MEASURES}
            sw = {m: paired(data, s, f'{ar} 80', f'{ar} 20', m) for m in MEASURES}
            swing[(s, ar)] = (hi, lo, sw)
            L.append(f"| {ar} | {f(hi['xPts'])} | {hi['xGF'][0]:+.3f} | {hi['xGA'][0]:+.3f} | {f(lo['xPts'])} | {lo['xGF'][0]:+.3f} | {lo['xGA'][0]:+.3f} | "
                     f"{f(sw['xPts'])} | {f(sw['xGD'])} | {hi['xPts'][3]} |")
        for m in ('xPts', 'xGD'):
            v = [swing[(s, ar)][2][m] for ar in AREAS]; w = [1 / e[2] ** 2 for e in v]
            mean = sum(x[0] * wi for x, wi in zip(v, w)) / sum(w); q = sum(wi * (x[0] - mean) ** 2 for x, wi in zip(v, w))
            L.append(f"\nAreas equal ({m} swing)? chi-square {q:.1f} on 7 df, p {chi2_sf(q, 7):.3f}; weighted mean swing {mean:+.3f}.")
        rank = sorted(AREAS, key=lambda ar: -swing[(s, ar)][2]['xPts'][0])
        L += ['', 'Ranked by the xPts swing: ' + ', '.join(f"{i + 1}. {ar} ({swing[(s, ar)][2]['xPts'][0]:+.3f})" for i, ar in enumerate(rank)), '']
    if len(styles) == 2:
        s0, s1 = styles; L += ['## Do the styles rank the areas alike?', '']
        for m in ('xPts', 'xGD'):
            for k, label in ((2, 'swing'), (0, 'at 80'), (1, 'at 20')):
                z = [(swing[(s0, ar)][k][m][0] - swing[(s1, ar)][k][m][0]) / math.hypot(swing[(s0, ar)][k][m][2], swing[(s1, ar)][k][m][2]) for ar in AREAS]
                q = sum(x * x for x in z)
                rho = spearman([swing[(s0, ar)][k][m][0] for ar in AREAS], [swing[(s1, ar)][k][m][0] for ar in AREAS])
                L.append(f"- {m} {label}: styles differ chi-square {q:.1f} on 8 df (p {chi2_sf(q, 8):.3f}); rank correlation {rho:+.2f}; "
                         f"largest difference {AREAS[max(range(8), key=lambda i: abs(z[i]))]} (z {max(z, key=abs):+.1f})")
        L.append('')
    text = '\n'.join(L) + '\n'; (out / 'areas.md').write_text(text); print(text)


if __name__ == '__main__':
    main()
