"""Study 25a: every part of tactical familiarity at every level, at random, together.

  python port/validation/study25_familiarity.py build OUT --from runs/study24 [--configs Gegenpress=3125,"Control Possession"=1875] [--seed 25]
  python port/validation/study25_familiarity.py run OUT [--workers 7] [--pilot]
  python port/validation/study25_familiarity.py report OUT          # OUT/report.md, OUT/effects.json

Eleven parts are varied on the tested side: the eight tactical areas, the overall value, buy-in and next-match
information. In each configuration every part gets one of eight values at random, independently, one inside each step
the match engine distinguishes (VALUES); the value is the same for every player of the side. The opponent's eight areas
get one of three values (OPP_VALUES), so the study also shows whether the other side's familiarity matters as much.

The areas' values are set exactly: the player's tactical ability is set to 0 and the tactic's complexity to 100, so an
area's value depends only on its training and match-exposure bytes (byte_for). Overall, buy-in and next-match are
written directly. The host re-applies the values whenever the engine rebuilds the record, so they hold for the match.

Every configuration is played on Study 24's 16 unchanged settings per style (four opponents, home and away, two
templates) with its own seed. A regression per style with seven indicators per part (each value against 45, where
the area neither helps nor hurts), two for the opponent, and a constant per setting gives every part's full
response from every match. Interactions between areas are tested on top of it.
"""
import argparse, functools, json, math, random, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for p in ('port/validation', 'port/map', 'src'): sys.path.insert(0, str(ROOT / p))
import league
from random_study import chi2_sf
from study24_areas import AREAS

VALUES = (8, 25, 37, 45, 58, 73, 85, 95)          # one per step the engine distinguishes
REF = VALUES.index(45)                             # the reference: the area neither helps nor hurts
OPP_VALUES = (37, 58, 85)
PARTS = AREAS + ['Overall', 'Buy-in', 'Next-match information']
DIRECT = {'Overall': 0x1e, 'Buy-in': 0x1f, 'Next-match information': 0x20}
MEASURES = ('xPts', 'xGF', 'xGA', 'xGD', 'pts', 'GF', 'GA')


@functools.cache
def byte_for(target):
    """(training, exposure) bytes that give an area exactly this value, with ability 0 and complexity 100 (the two
    bytes as close as possible to each other)."""
    import exec_record as er
    best = None
    for t1 in range(128):
        for t2 in range(128):
            rec = bytearray(34); rec[0x21] = 4; rec[0x19] = rec[0x1a] = rec[0x1b] = 100; rec[2], rec[3] = t1, t2
            if er.value(bytes(rec), 3) == target and (best is None or abs(t1 - t2) < abs(best[0] - best[1])): best = (t1, t2)
    if best is None: raise SystemExit(f'no bytes give value {target}')
    return best


def fields(levels, opp, side):
    """levels: 11 band indices for the tested side; opp: band index into OPP_VALUES for the other side."""
    out = []
    for x in (0, 1):
        if x == side:
            for k in range(8):   # a triple: an unread byte, training, match exposure
                t1, t2 = byte_for(VALUES[levels[k]]); out += [f'{x}:{1 + 3 * k}={t1}', f'{x}:{2 + 3 * k}={t1}', f'{x}:{3 + 3 * k}={t2}']
            out += [f'{x}:{DIRECT[p]}={VALUES[levels[8 + i]]}' for i, p in enumerate(PARTS[8:])]
        else:
            t1, t2 = byte_for(OPP_VALUES[opp]); out += [f'{x}:{1 + 3 * k + j}={(t1, t1, t2)[j]}' for k in range(8) for j in range(3)]
        out += [f'{x}:0=0'] + [f'{x}:{o}=100' for o in (0x19, 0x1a, 0x1b)]
    return {'FM27_MAC_EXEC_FIELDS': ','.join(out)}


def build(a):
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    configs = {k: int(v) for k, v in (x.split('=') for x in a.configs.split(','))}
    base = [j for j in json.loads((Path(a.source) / 'jobs_all.json').read_text()) if j[1].split('|')[1] == 'none']
    settings = {}
    for j in base:   # one scenario per (style, opponent, venue, template)
        style, _, opp, venue, k = j[1].split('|'); settings.setdefault(style, {})[(opp, int(venue), int(k))] = (j[2], j[3])
    rng = random.Random(a.seed); jobs, design = [], {}
    for style, n in configs.items():
        sets = settings[style]
        for c in range(n):
            levels = [rng.randrange(len(VALUES)) for _ in PARTS]; opp = rng.randrange(len(OPP_VALUES))
            design[f'{style}|{c}'] = {'levels': levels, 'opp': opp}
            for (o, venue, k), (path, b) in sorted(sets.items()):
                jobs.append(['N', f'{style}|R{c}|{o}|{venue}|{k}', path, b, fields(levels, opp, venue), 1, 200000 + c])
    order = random.Random(a.seed + 1); order.shuffle(jobs)   # styles and configurations interleaved: a stopped run is still balanced
    (out / 'jobs_all.json').write_text(json.dumps(jobs)); (out / 'design.json').write_text(json.dumps(design))
    (out / 'meta.json').write_text(json.dumps({'title': 'Study 25a: tactical familiarity, every part at every level', 'source': str(Path(a.source).resolve()),
                                               'configs': configs, 'values': VALUES, 'opp_values': OPP_VALUES, 'parts': PARTS, 'seed': a.seed,
                                               'bytes': {v: byte_for(v) for v in VALUES}}, indent=1))
    print(len(jobs), 'matches,', len(design), 'configurations; area bytes', {v: byte_for(v) for v in VALUES})


def run(a):
    import overnight
    out = Path(a.out).resolve(); jobs = json.loads((out / 'jobs_all.json').read_text())
    if a.pilot:   # the first 10 configurations of each style
        jobs = [j for j in jobs if int(j[1].split('|')[1][1:]) < 10]
    (out / 'jobs.json').write_text(json.dumps(jobs)); overnight.run(out, a.workers)
    if a.pilot:
        got = sum(1 for _ in open(out / 'results.jsonl')); print(f'pilot: {got} results for {len(jobs)} matches;', 'PASS' if got >= len(jobs) else 'FAIL')


def matrix(out, style):
    """Rows of (design row, setting, outcomes) for one style; X: 77 part indicators + 2 opponent + settings."""
    import numpy as np, neutral_study as ns
    design = json.loads((out / 'design.json').read_text()); data = ns.load(out)
    rows = [(design[f'{style}|{c[1:]}'], key, v) for (g, c), d in data.items() if g == style for key, v in d.items()]
    setkeys = sorted({key[:3] for _, key, _ in rows}); si = {s: i for i, s in enumerate(setkeys)}
    nb = len(VALUES) - 1; P = len(PARTS) * nb + 2
    X = np.zeros((len(rows), P + len(setkeys)))
    for r, (d, key, _) in enumerate(rows):
        for k, lv in enumerate(d['levels']):
            if lv != REF: X[r, k * nb + (lv if lv < REF else lv - 1)] = 1
        if d['opp'] != 1: X[r, len(PARTS) * nb + (0 if d['opp'] == 0 else 1)] = 1   # opponent against 58
        X[r, P + si[key[:3]]] = 1
    return rows, X, P


def ols(X, y):
    import numpy as np
    XtX = X.T @ X
    if np.linalg.matrix_rank(XtX) < X.shape[1]: raise SystemExit('too few configurations so far for the regression')
    b = np.linalg.solve(XtX, X.T @ y); e = y - X @ b
    return b, np.linalg.inv(XtX) * (e @ e / (len(y) - X.shape[1]))


def wald(b, C, idx):
    import numpy as np
    v = b[idx]; return float(v @ np.linalg.solve(C[np.ix_(idx, idx)], v)), len(idx)


def report(a):
    import numpy as np
    out = Path(a.out); design = json.loads((out / 'design.json').read_text()); styles = sorted({k.split('|')[0] for k in design})
    nb = len(VALUES) - 1; bands = [v for i, v in enumerate(VALUES) if i != REF]
    L = ['# Study 25a: tactical familiarity, every part at every level', '',
         'Per game; each value against 45 (where the area neither helps nor hurts), with every other part at random. '
         't in brackets.', '']
    eff = {}
    for s in styles:
        rows, X, P = matrix(out, s); res = {}
        for m in MEASURES:
            y = np.array([v[m] for _, _, v in rows], float); res[m] = ols(X, y)
        L += [f'## {s} ({len(rows)} matches, {len({id(d) for d, _, _ in rows})} configurations)', '',
              '**Expected points by value** (per game, against value 45):', '',
              '| Part | ' + ' | '.join(str(v) for v in bands) + ' | Matters? (7 df) |', '|---|' + '---|' * (nb + 1)]
        for k, part in enumerate(PARTS):
            b, C = res['xPts']; idx = list(range(k * nb, (k + 1) * nb)); q, df = wald(b, C, idx)
            cells = [f'{b[i]:+.3f} ({b[i] / math.sqrt(C[i, i]):+.1f})' for i in idx]
            L.append(f'| {part} | ' + ' | '.join(cells) + f' | chi-square {q:.0f}, p {chi2_sf(q, df):.4f} |')
            for m in MEASURES:
                bm, Cm = res[m]; eff[f'{s}|{part}|{m}'] = [[float(bm[i]), float(math.sqrt(Cm[i, i]))] for i in idx]
        b, C = res['xPts']; o = len(PARTS) * nb
        L += ['', f"Opponent's areas (against 58): at 37 {b[o]:+.3f} ({b[o] / math.sqrt(C[o, o]):+.1f}), "
              f"at 85 {b[o + 1]:+.3f} ({b[o + 1] / math.sqrt(C[o + 1, o + 1]):+.1f}).", '']
        for m in ('xPts', 'xGD', 'xGF', 'xGA', 'GA'):
            bm, Cm = res[m]; eff[f'{s}|opponent|{m}'] = [[float(bm[o + i]), float(math.sqrt(Cm[o + i, o + i]))] for i in (0, 1)]
        L += ['**From the worst to the best value** (8 against 95; xG for, xG against, goals against):', '',
              '| Part | xPts 8 | xPts 37 | xPts 95 | xG for 37 | xG against 37 | xG for 95 | xG against 95 |', '|---|---|---|---|---|---|---|---|']
        col = lambda v: VALUES.index(v) if VALUES.index(v) < REF else VALUES.index(v) - 1
        for k, part in enumerate(PARTS):
            f = lambda m, v: (lambda i: f'{res[m][0][i]:+.3f}')(k * nb + col(v))
            L.append(f"| {part} | {f('xPts', 8)} | {f('xPts', 37)} | {f('xPts', 95)} | {f('xGF', 37)} | {f('xGA', 37)} | {f('xGF', 95)} | {f('xGA', 95)} |")
        # interactions: each area's step effect times another's, all 28 pairs
        # step scale: the engine's own (git-ignored private/engine_steps.json, a list of 8) if present, else the step number
        sf = ROOT / 'private/engine_steps.json'
        F = json.loads(sf.read_text()) if sf.exists() else [i - REF + 1 for i in range(len(VALUES))]
        Z = np.array([[F[d['levels'][k]] - 1 for k in range(8)] for d, _, _ in rows])
        pairs = [(i, j) for i in range(8) for j in range(i + 1, 8)]
        XI = np.hstack([X, np.stack([Z[:, i] * Z[:, j] for i, j in pairs], 1)])
        y = np.array([v['xPts'] for _, _, v in rows], float); bi, Ci = ols(XI, y); base = X.shape[1]
        q, df = wald(bi, Ci, list(range(base, base + len(pairs))))
        L += ['', f'**Do the areas combine additively?** All 28 pairwise interactions (on the steps): chi-square {q:.0f} on {df}, p {chi2_sf(q, df):.3f}.', '']
        top = sorted(range(len(pairs)), key=lambda t: -abs(bi[base + t] / math.sqrt(Ci[base + t, base + t])))[:6]
        for t in top:
            i, j = pairs[t]; L.append(f'- {AREAS[i]} × {AREAS[j]}: {bi[base + t]:+.3f} per unit² (t {bi[base + t] / math.sqrt(Ci[base + t, base + t]):+.1f})')
        L.append('')
    if len(styles) == 2:
        s0, s1 = styles; L += ['## Do the styles differ?', '']
        for part in PARTS:
            z = [(p[0] - q[0]) / math.hypot(p[1], q[1]) for p, q in zip(eff[f'{s0}|{part}|xPts'], eff[f'{s1}|{part}|xPts'])]
            q = sum(x * x for x in z); L.append(f'- {part}: chi-square {q:.1f} on 7 (p {chi2_sf(q, 7):.3f})')
        L.append('')
    (out / 'effects.json').write_text(json.dumps(eff)); text = '\n'.join(L) + '\n'; (out / 'report.md').write_text(text); print(text)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    b = sub.add_parser('build'); b.add_argument('out'); b.add_argument('--from', dest='source', required=True)
    b.add_argument('--configs', default='Gegenpress=3125,Control Possession=1875'); b.add_argument('--seed', type=int, default=25)
    r = sub.add_parser('run'); r.add_argument('out'); r.add_argument('--workers', type=int, default=7); r.add_argument('--pilot', action='store_true')
    t = sub.add_parser('report'); t.add_argument('out')
    a = p.parse_args(); {'build': build, 'run': run, 'report': report}[a.cmd](a)


if __name__ == '__main__':
    main()
