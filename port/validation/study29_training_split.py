"""Study 29: two ways to split tactical-familiarity training, against a common opponent and head to head.

  python port/validation/study29_training_split.py build OUT --from runs/study24 [--seeds 100]
  python port/validation/study29_training_split.py check OUT          # one match per context: the record values
  python port/validation/study29_training_split.py run OUT [--workers 7]
  python port/validation/study29_training_split.py report OUT         # OUT/report.md

Scenario A trains Chance creation and Pressing intensity to 100 and four areas to 28; scenario B trains those two to
85 and the four to 42 (Pressing trap and Line of engagement 0 in both). "Training" is each area's training byte; an
area's value also depends on the player's tactical ability, the area's match exposure and the tactic's complexity,
and the engine reads the value in steps, so whether a split pays depends on that base. Three contexts
cover the realistic range (CONTEXTS); the players keep their own tactical ability.

Per context, Study 24's 32 settings (Gegenpress and Control Possession; four opponents, home and away; two templates),
each on the same seeds in four conditions: A and B against an opponent with every area trained to 41 (same context),
and A against B with the sides swapped (AvB: the tested side has A). Head to head, each pair of swapped matches
cancels home advantage and the squads.
"""
import argparse, json, math, random, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for p in ('port/validation', 'port/map', 'src'): sys.path.insert(0, str(ROOT / p))
from study24_areas import AREAS

SCENARIOS = {
    'A': {'Chance creation': 100, 'Pressing intensity': 100, 'Out-of-possession shape': 28, 'Passing style': 28,
          'Build-up': 28, 'In-possession shape': 28, 'Pressing trap': 0, 'Line of engagement': 0},
    'B': {'Chance creation': 85, 'Pressing intensity': 87, 'Out-of-possession shape': 42, 'Passing style': 42,
          'Build-up': 42, 'In-possession shape': 42, 'Pressing trap': 0, 'Line of engagement': 0},
    'C': {a: 42 for a in AREAS},
    'O': {a: 41 for a in AREAS}}
CONTEXTS = {   # name: (match exposure byte, tactic complexity)
    'complex-established': (100, 78), 'simple-established': (100, 30), 'complex-learning': (40, 78),
    'pies': None}   # the scenario's numbers are the area values themselves (the panel's pies), set exactly as in Study 25a
LABEL = {'complex-established': 'Complex tactic, fully learnt (complexity 78, full match exposure)',
         'simple-established': 'Simple tactic, fully learnt (complexity 30, full match exposure)',
         'complex-learning': 'Complex tactic, still being learnt (complexity 78, 40% match exposure)',
         'pies': 'Area values (the pies) set exactly, every player'}
CONDS = {'A': ('A', 'O'), 'B': ('B', 'O'), 'AvB': ('A', 'B'), 'BvA': ('B', 'A')}   # (tested side, other side)
PAIRS = [('A', 'B'), ('A', 'C'), ('B', 'C')]
for x, y in PAIRS: CONDS[f'{x}v{y}'] = (x, y); CONDS[f'{y}v{x}'] = (y, x)
H2H = [c for c in CONDS if 'v' in c]


def side_fields(x, scen, ctx):
    if CONTEXTS[ctx] is None:   # exact values: tactical ability 0, complexity 100, (training, exposure) from byte_for
        from study25_familiarity import byte_for
        out = []
        for k, area in enumerate(AREAS):
            t1, t2 = byte_for(SCENARIOS[scen][area]); out += [f'{x}:{1 + 3 * k}={t1}', f'{x}:{2 + 3 * k}={t1}', f'{x}:{3 + 3 * k}={t2}']
        return out + [f'{x}:0=0'] + [f'{x}:{o}=100' for o in (0x19, 0x1a, 0x1b)]
    t2, T = CONTEXTS[ctx]; out = []
    for k, area in enumerate(AREAS):   # a triple: an unread byte, training, match exposure
        t1 = SCENARIOS[scen][area]; out += [f'{x}:{1 + 3 * k}={t1}', f'{x}:{2 + 3 * k}={t1}', f'{x}:{3 + 3 * k}={t2}']
    return out + [f'{x}:{o}={T}' for o in (0x19, 0x1a, 0x1b)]


def fields(cond, ctx, venue):
    me, other = CONDS[cond]
    return {'FM27_MAC_EXEC_FIELDS': ','.join(side_fields(venue, me, ctx) + side_fields(1 - venue, other, ctx))}


def build(a):
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    base = [j for j in json.loads((Path(a.source) / 'jobs_all.json').read_text()) if j[1].split('|')[1] == 'none']
    jobs, settings = [], {}
    for j in base:   # Study 24 lists each seed as its own job: one per setting
        style, _, opp, venue, k = j[1].split('|'); settings.setdefault((style, opp, venue, k), j)
    for (style, opp, venue, k), j in sorted(settings.items()):
        for ctx in a.contexts.split(','):
            for cond in (H2H if a.h2h else CONDS):
                jobs.append(['N', f'{ctx}|{cond}|{style}|{opp}|{venue}|{k}', j[2], j[3], fields(cond, ctx, int(venue)), a.seeds, 290001])
    random.Random(29).shuffle(jobs)
    (out / 'jobs_all.json').write_text(json.dumps(jobs))
    (out / 'meta.json').write_text(json.dumps({'title': 'Study 29: two training splits', 'scenarios': SCENARIOS,
                                               'contexts': CONTEXTS, 'seeds': a.seeds, 'source': str(Path(a.source).resolve())}, indent=1))
    print(len(jobs), 'jobs,', len(jobs) * a.seeds, 'matches')


def check(a):
    """Play one match per context (AvB) with the record summary on and compare every player's area values with the
    accessor formula, at the finished stage."""
    import os, subprocess, tempfile, exec_record as er, overnight
    out = Path(a.out); jobs = json.loads((out / 'jobs_all.json').read_text()); ok = True
    for ctx in CONTEXTS:
        j = next((j for j in jobs if j[1].startswith(f'{ctx}|AvC|')), None)
        if j is None: continue
        venue = int(j[1].split('|')[4]); env = dict(os.environ, FM27_MAC_RECORD_SUMMARY='1', **j[4])
        with tempfile.TemporaryDirectory() as d:
            o = Path(d) / 'm.jsonl'
            subprocess.run([str(overnight.HOST), '--fixture', str(Path(j[2]).resolve()), '--scenario-file', str(Path(j[3]).resolve()),
                            '--seed', '290001', '--output', str(o)], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=600)
            ev = [json.loads(l) for l in open(o) if 'research_record_summary' in l]
        fin = [e for e in ev if e['stage'] == 'finished']
        if not fin: print(ctx, 'no finished-stage record'); ok = False; continue
        for e in fin[-2:]:
            scen = 'A' if e['side'] == venue else 'C'
            vals = [[er.value(bytes.fromhex(p[6]), c) for c in (3, 4, 5, 6, 0, 1, 2, 7)] for p in e['players']]
            want = []
            if CONTEXTS[ctx] is None: want = [[SCENARIOS[scen][a] for a in AREAS] for _ in e['players']]
            for p in ([] if CONTEXTS[ctx] is None else e['players']):
                rec = bytearray(bytes.fromhex(p[6]))
                for k, area in enumerate(AREAS):
                    t2, T = CONTEXTS[ctx]; rec[1 + 3 * k] = rec[2 + 3 * k] = SCENARIOS[scen][area]; rec[3 + 3 * k] = t2
                rec[0x19] = rec[0x1a] = rec[0x1b] = CONTEXTS[ctx][1]
                want.append([er.value(bytes(rec), c) for c in (3, 4, 5, 6, 0, 1, 2, 7)])
            good = vals == want; ok &= good
            print(f"{ctx} side {e['side']} ({scen}): {'OK' if good else 'MISMATCH'}; ability",
                  [bytes.fromhex(p[6])[0] for p in e['players']], 'areas of player 1', vals[1])
    print('PASS' if ok else 'FAIL')


def run(a):
    import overnight
    out = Path(a.out).resolve(); (out / 'jobs.json').write_text((out / 'jobs_all.json').read_text()); overnight.run(out, a.workers)


def load(out):
    """{(ctx, cond, style, opp, venue, k, seed): (xPts of tested side, of other side, goals for, against, xGD)}"""
    import league
    res = {}
    for line in open(out / 'results.jsonl'):
        r = json.loads(line); ctx, cond, style, opp, venue, k = r['cond'].split('|'); me = int(venue)
        xm, xo = league.xpts(r['xg'][me], r['xg'][1 - me]), league.xpts(r['xg'][1 - me], r['xg'][me])
        res[(ctx, cond, style, opp, venue, k, r['seed'])] = (xm, xo, r['score'][me], r['score'][1 - me], r['xg'][me] - r['xg'][1 - me])
    return res


def stat(x):
    n = len(x); m = sum(x) / n; sd = math.sqrt(sum((v - m) ** 2 for v in x) / (n - 1)); return m, sd / math.sqrt(n), n


def h2h_report(a):
    out = Path(a.out); res = load(out)
    pts = lambda g, h: 3 if g > h else 1 if g == h else 0
    L = ['# Study 29: two ways to split familiarity training, head to head', '',
         'Each pairing plays every match-up twice on the same seed, with the sides swapped. "Edge" = the second '
         'scenario minus the first in one meeting (expected points or xG difference), averaged over the swapped pair. '
         't in brackets; season = ×38.', '']
    for k, v in json.loads((out / 'meta.json').read_text())['scenarios'].items():
        if k != 'O': L.append(f'- **{k}:** ' + ', '.join(f'{a} {x}' for a, x in v.items()))
    L.append('')
    summary = {}
    for ctx in sorted({k[0] for k in res}):
        L += [f'## {LABEL[ctx]}', '', '| Pairing | Style | xPts edge per game | per season | xG difference edge | points edge | wins / draws / losses (second scenario) |', '|---|---|---|---|---|---|---|']
        for x, y in PAIRS:
            for style in ('Gegenpress', 'Control Possession', 'both'):
                sts = ('Gegenpress', 'Control Possession') if style == 'both' else (style,)
                ex, eg, ep, w = [], [], [], [0, 0, 0]
                for k, r1 in res.items():   # r1: x on the tested side; r2: y on the tested side, same match-up and seed
                    if k[0] != ctx or k[1] != f'{x}v{y}' or k[2] not in sts: continue
                    r2 = res.get((ctx, f'{y}v{x}') + k[2:])
                    if not r2: continue
                    ex.append(((r1[1] - r1[0]) + (r2[0] - r2[1])) / 2); eg.append((-r1[4] + r2[4]) / 2)
                    ep.append(((pts(r1[3], r1[2]) - pts(r1[2], r1[3])) + (pts(r2[2], r2[3]) - pts(r2[3], r2[2]))) / 2)
                    for g, h in ((r1[3], r1[2]), (r2[2], r2[3])): w[0 if g > h else 1 if g == h else 2] += 1
                if len(ex) < 2: continue
                sx, sg, sp = stat(ex), stat(eg), stat(ep); tw = sum(w)
                f = lambda s: f'{s[0]:+.3f} ({s[0] / s[1]:+.1f})'
                L.append(f"| {y} vs {x} | {style} | {f(sx)} | {38 * sx[0]:+.1f} ± {38 * 1.96 * sx[1]:.1f} | {f(sg)} | {f(sp)} | "
                         f"{100 * w[0] / tw:.0f}% / {100 * w[1] / tw:.0f}% / {100 * w[2] / tw:.0f}% ({sx[2]} pairs) |")
                summary[f'{ctx}|{y}v{x}|{style}'] = {'xPts': sx, 'xGD': sg, 'pts': sp, 'wins': w}
        L.append('')
    (out / 'summary.json').write_text(json.dumps(summary)); text = '\n'.join(L) + '\n'; (out / 'report.md').write_text(text); print(text)


def report(a):
    if not any(json.loads(l)['cond'].split('|')[1] in ('A', 'B') for l in open(Path(a.out) / 'results.jsonl')): return h2h_report(a)
    out = Path(a.out); res = load(out); L = ['# Study 29: two ways to split familiarity training', '',
        'B minus A, per game (t in brackets). Season = ×38.', '',
        'A: Chance creation and Pressing intensity 100, four areas 28. B: those two 85, the four 42. Pressing trap and Line of engagement 0 in both.', '']
    summary = {}
    for scope in list(CONTEXTS) + ['all']:
        ctxs = list(CONTEXTS) if scope == 'all' else [scope]
        rows = []
        for style in ('Gegenpress', 'Control Possession', 'both'):
            sts = ('Gegenpress', 'Control Possession') if style == 'both' else (style,)
            keys = [k for k in res if k[0] in ctxs and k[2] in sts and k[1] == 'A']
            neut = {m: [] for m in ('xPts', 'xGD', 'pts')}; h2h = {m: [] for m in ('xPts', 'xGD', 'pts')}; w = [0, 0, 0]
            for k in keys:
                b = res.get((k[0], 'B') + k[2:])
                if b:
                    av = res[k]; pts = lambda r: 3 if r[2] > r[3] else 1 if r[2] == r[3] else 0
                    neut['xPts'].append(b[0] - av[0]); neut['xGD'].append(b[4] - av[4]); neut['pts'].append(pts(b) - pts(av))
                ab, ba = res.get((k[0], 'AvB') + k[2:]), res.get((k[0], 'BvA') + k[2:])
                if ab and ba:   # B's edge: (B - A) in each of the two matches, averaged
                    h2h['xPts'].append(((ab[1] - ab[0]) + (ba[0] - ba[1])) / 2); h2h['xGD'].append((-ab[4] + ba[4]) / 2)
                    pa = lambda r: (3 if r[2] > r[3] else 1 if r[2] == r[3] else 0) - (3 if r[3] > r[2] else 1 if r[2] == r[3] else 0)
                    h2h['pts'].append((-pa(ab) + pa(ba)) / 2)
                    for r, bside in ((ab, 1), (ba, 0)):
                        gb, ga = (r[3], r[2]) if bside else (r[2], r[3]); w[0 if gb > ga else 1 if gb == ga else 2] += 1
            if not neut['xPts']: continue
            rows.append((style, {m: stat(v) for m, v in neut.items()}, {m: stat(v) for m, v in h2h.items()} if h2h['xPts'] else None, w))
        if not rows: continue
        L += [f"## {'All three contexts' if scope == 'all' else LABEL[scope]}", '',
              '| Style | vs common opponent: xPts | xGD | points | head to head: xPts edge | xGD | points edge | B wins / draws / A wins |', '|---|---|---|---|---|---|---|---|']
        for style, n, h, w in rows:
            f = lambda s: f'{s[0]:+.3f} ({s[0] / s[1]:+.1f})' if s[1] > 0 else f'{s[0]:+.3f}'
            hh = ' | '.join(f(h[m]) for m in ('xPts', 'xGD', 'pts')) if h else '| |'
            tw = sum(w) or 1
            L.append(f"| {style} | {f(n['xPts'])} | {f(n['xGD'])} | {f(n['pts'])} | {hh} | {100 * w[0] / tw:.0f}% / {100 * w[1] / tw:.0f}% / {100 * w[2] / tw:.0f}% |")
            summary[f'{scope}|{style}'] = {'neutral': n, 'h2h': h, 'wins': w}
        L += [f"Pairs: {rows[-1][1]['xPts'][2]} against the common opponent, {rows[-1][2]['xPts'][2] if rows[-1][2] else 0} head to head.", '']
    (out / 'summary.json').write_text(json.dumps(summary)); text = '\n'.join(L) + '\n'; (out / 'report.md').write_text(text); print(text)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter); sub = ap.add_subparsers(dest='cmd', required=True)
    b = sub.add_parser('build'); b.add_argument('out'); b.add_argument('--from', dest='source', default='runs/study24'); b.add_argument('--seeds', type=int, default=100)
    b.add_argument('--contexts', default=','.join(CONTEXTS)); b.add_argument('--h2h', action='store_true', help='head-to-head conditions only')
    c = sub.add_parser('check'); c.add_argument('out')
    r = sub.add_parser('run'); r.add_argument('out'); r.add_argument('--workers', type=int, default=7)
    p = sub.add_parser('report'); p.add_argument('out')
    a = ap.parse_args(); {'build': build, 'check': check, 'run': run, 'report': report}[a.cmd](a)


if __name__ == '__main__':
    main()
