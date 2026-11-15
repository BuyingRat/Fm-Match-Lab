"""Study 24b: the eight tactical familiarity areas at random levels, to measure each area far more precisely than
one area at a time (Study 24).

  python port/validation/study24b_random_areas.py build OUT --from runs/study24 [--configs 850] [--seed 24]
  python port/validation/study24b_random_areas.py run OUT [--workers 7] [--pilot]
  python port/validation/study24b_random_areas.py report OUT          # OUT/report.md

Each configuration gives each of the tested side's eight areas a level of 20, 50 or 80 at random (independently) and
is played on every setting of Study 24 (its unchanged scenarios: four opponents, home and away, two templates; the
opponent's areas at 50) with its own seed. A regression per style on two indicators per area (at 20, at 80; 50 is the
reference) and a constant per setting gives each area's effect of lowering and of raising, from every match.
Pairing on seeds is not used: in Study 24 a changed area made the same seed's match no more alike than another match.
"""
import argparse, json, math, random, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'port/validation')); sys.path.insert(0, str(ROOT / 'src'))
import league
from random_study import chi2_sf
from study24_areas import AREAS

LEVELS = (20, 50, 80)
MEASURES = ('xPts', 'xGF', 'xGA', 'xGD', 'pts')


def fields(levels, side):
    lv = {(side, 1 + 3 * k + j): levels[k] for k in range(8) for j in range(3)}
    return {'FM27_MAC_EXEC_FIELDS': ','.join(f'{x}:{o}={lv.get((x, o), 50)}' for x in (0, 1) for o in league.AREAS) + ',' +
            ','.join(f'{x}:{o}=50' for x in (0, 1) for o in (0x19, 0x1a))}


def build(a):
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    base = [j for j in json.loads((Path(a.source) / 'jobs_all.json').read_text()) if j[1].split('|')[1] == 'none']
    settings = {}
    for j in base:   # one scenario per (style, opponent, venue, template)
        style, _, opp, venue, k = j[1].split('|'); settings.setdefault(style, {})[(opp, int(venue), int(k))] = (j[2], j[3])
    rng = random.Random(a.seed); jobs, design = [], {}
    for style, sets in settings.items():
        for c in range(a.configs):
            levels = [rng.choice(LEVELS) for _ in AREAS]; design[f'{style}|{c}'] = levels
            for (opp, venue, k), (path, b) in sorted(sets.items()):
                jobs.append(['N', f'{style}|R{c}|{opp}|{venue}|{k}', path, b, fields(levels, venue), 1, 100000 + c])
    (out / 'jobs_all.json').write_text(json.dumps(jobs)); (out / 'design.json').write_text(json.dumps(design))
    (out / 'meta.json').write_text(json.dumps({'title': 'Study 24b: familiarity areas at random levels', 'source': str(Path(a.source).resolve()),
                                               'configs': a.configs, 'levels': LEVELS, 'areas': AREAS, 'seed': a.seed}, indent=1))
    print(len(jobs), 'matches,', len(design), 'configurations')


def run(a):
    import overnight
    out = Path(a.out).resolve(); jobs = json.loads((out / 'jobs_all.json').read_text())
    if a.pilot:   # the first 10 configurations of each style
        jobs = [j for j in jobs if int(j[1].split('|')[1][1:]) < 10]
    (out / 'jobs.json').write_text(json.dumps(jobs)); overnight.run(out, a.workers)
    if a.pilot:
        got = sum(1 for _ in open(out / 'results.jsonl')); print(f'pilot: {got} results for {len(jobs)} matches;', 'PASS' if got >= len(jobs) else 'FAIL')


def analyse(out):
    import numpy as np
    import neutral_study as ns
    design = json.loads((out / 'design.json').read_text()); data = ns.load(out); res = {}
    for style in sorted({k.split('|')[0] for k in design}):
        rows = [(int(c[1:]), key, v) for (g, c), d in data.items() if g == style for key, v in d.items()]
        setkeys = sorted({key[:3] for _, key, _ in rows}); si = {s: i for i, s in enumerate(setkeys)}
        X = np.zeros((len(rows), 16 + len(setkeys)))
        for r, (c, key, _) in enumerate(rows):
            lv = design[f'{style}|{c}']
            for k in range(8):
                if lv[k] == 20: X[r, 2 * k] = 1
                if lv[k] == 80: X[r, 2 * k + 1] = 1
            X[r, 16 + si[key[:3]]] = 1
        res[style] = {'n': len(rows)}
        for m in MEASURES:
            y = np.array([v[m] for _, _, v in rows], float)
            XtX = X.T @ X
            if np.linalg.matrix_rank(XtX) < X.shape[1]: raise SystemExit(f'{style}: too few configurations so far for the regression')
            b = np.linalg.solve(XtX, X.T @ y); e = y - X @ b
            cov = np.linalg.inv(XtX) * (e @ e / (len(y) - X.shape[1]))
            res[style][m] = {'b': b[:16].tolist(), 'cov': cov[:16, :16].tolist()}
    return res


def report(a):
    import numpy as np
    out = Path(a.out); res = analyse(out); styles = list(res)
    L = ['# Study 24b: familiarity areas at random levels', '',
         'Per game; t in brackets. Lower = area at 20 instead of 50, raise = at 80 instead of 50, swing = 80 minus 20, '
         'each with the other areas at random levels.', '']
    eff = {}
    for s in styles:
        L += [f"## {s} ({res[s]['n']} matches)", '', '| Area | Lower: xPts | Raise: xPts | Swing: xPts | Swing: xG for | Swing: xG against | Swing: xG difference |',
              '|---|---|---|---|---|---|---|']
        for k, ar in enumerate(AREAS):
            row = []
            for m in MEASURES:
                b = np.array(res[s][m]['b']); C = np.array(res[s][m]['cov'])
                lo, hi = b[2 * k], b[2 * k + 1]; slo, shi = math.sqrt(C[2 * k, 2 * k]), math.sqrt(C[2 * k + 1, 2 * k + 1])
                sw = hi - lo; ssw = math.sqrt(C[2 * k, 2 * k] + C[2 * k + 1, 2 * k + 1] - 2 * C[2 * k, 2 * k + 1])
                eff[(s, ar, m)] = {'lower': (lo, slo), 'raise': (hi, shi), 'swing': (sw, ssw)}
            e = lambda m, w: f'{eff[(s, ar, m)][w][0]:+.3f} ({eff[(s, ar, m)][w][0] / eff[(s, ar, m)][w][1]:+.1f})'
            L.append(f"| {ar} | {e('xPts', 'lower')} | {e('xPts', 'raise')} | {e('xPts', 'swing')} | {e('xGF', 'swing')} | {e('xGA', 'swing')} | {e('xGD', 'swing')} |")
        for m in ('xPts', 'xGD'):
            for w in ('swing', 'lower', 'raise'):
                v = [eff[(s, ar, m)][w] for ar in AREAS]; wt = [1 / x[1] ** 2 for x in v]
                mean = sum(x[0] * q for x, q in zip(v, wt)) / sum(wt); q = sum(q * (x[0] - mean) ** 2 for x, q in zip(v, wt))
                L.append(f'\n{m} {w}: areas equal? chi-square {q:.1f} on 7 df, p {chi2_sf(q, 7):.4f}; mean {mean:+.3f}.')
        rank = sorted(AREAS, key=lambda ar: -eff[(s, ar, 'xPts')]['swing'][0])
        L += ['', 'Ranked by the xPts swing: ' + ', '.join(f"{i + 1}. {ar} ({eff[(s, ar, 'xPts')]['swing'][0]:+.3f})" for i, ar in enumerate(rank)), '']
    if len(styles) == 2:
        s0, s1 = styles; L += ['## Do the styles differ?', '']
        for m in ('xPts', 'xGD'):
            for w in ('swing', 'lower', 'raise'):
                z = [(eff[(s0, ar, m)][w][0] - eff[(s1, ar, m)][w][0]) / math.hypot(eff[(s0, ar, m)][w][1], eff[(s1, ar, m)][w][1]) for ar in AREAS]
                q = sum(x * x for x in z); i = max(range(8), key=lambda i: abs(z[i]))
                L.append(f'- {m} {w}: chi-square {q:.1f} on 8 df (p {chi2_sf(q, 8):.4f}); largest difference {AREAS[i]} (z {z[i]:+.1f})')
        L.append('')
    (out / 'effects.json').write_text(json.dumps({f'{s}|{ar}|{m}': v for (s, ar, m), v in eff.items()}))
    text = '\n'.join(L) + '\n'; (out / 'report.md').write_text(text); print(text)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    b = sub.add_parser('build'); b.add_argument('out'); b.add_argument('--from', dest='source', required=True)
    b.add_argument('--configs', type=int, default=850); b.add_argument('--seed', type=int, default=24)
    r = sub.add_parser('run'); r.add_argument('out'); r.add_argument('--workers', type=int, default=7); r.add_argument('--pilot', action='store_true')
    t = sub.add_parser('report'); t.add_argument('out')
    a = p.parse_args(); {'build': build, 'run': run, 'report': report}[a.cmd](a)


if __name__ == '__main__':
    main()
