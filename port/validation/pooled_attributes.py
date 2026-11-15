"""Attribute evidence across studies: does the random-configuration model (Study 13b) predict the conditions measured
one at a time in the roadmap studies, and what do all studies say together?

  python port/validation/pooled_attributes.py designs OUT              # each roadmap condition's changes, per starter
  python port/validation/pooled_attributes.py predict OUT [--random runs/random/gegenpress]   # OUT/predict.md

'designs' rebuilds every roadmap condition played in Study 13b's set-up (Gegenpress, the Premier League middle-eight
squad on both sides, familiarity 80, the default templates and opponents) on one setting and records what it changes:
levels per starter and field, plus anything the random study did not vary (subs, the opponent, position ratings,
morale, Current Ability), which marks the condition as out of the model's scope or only partly in it.

'predict' compares each condition's measured effect (paired against its study's unchanged side, as reported) with the
random model's prediction: the sum over starters and fields of the per-level coefficient for that position and field
times the change in levels. A linear, additive model predicts every condition; where it misses shows thresholds,
diminishing returns or combinations.
"""
import argparse, copy, json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for p in ('scripts', 'src', 'port/validation'): sys.path.insert(0, str(ROOT / p))

STUDIES = ['09b', '10', '11', '12', '13', '14', '14b', '20', '21', '21b']
MEASURES = ('xPts', 'xGD', 'pts', 'GA', 'xGA', 'GF', 'xGF')


def designs(a):
    import study, league, neutral_study as ns, roadmap_studies as rs, random_study as rnd
    A = study.app(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    F = rnd.fields(); by_key = {(k, key): rnd.nice(label) for label, k, key in F}
    path = ns.template_path(ns.DEFAULT_TEMPLATES[0]); base = league.same_squad_size(A.validate_scenario(A.SAVED_MATCHES.open(path).default))
    b = league.Builder(A, out / 'scratch'); venue = 0; result = {}
    for name in STUDIES:
        spec = rs.STUDIES[name]()
        if spec.get('familiarity', 80) != 80: continue
        for g in spec['groups']:
            if (g.get('style') != 'Gegenpress' or g.get('tier', 'pl-middle') != 'pl-middle' or g.get('opp_tier', g.get('tier', 'pl-middle')) != 'pl-middle'
                    or g.get('instructions') or g.get('setup') or g.get('templates', ns.DEFAULT_TEMPLATES) != ns.DEFAULT_TEMPLATES
                    or list(g.get('panel', ns.PANEL)) != ns.PANEL):
                continue
            s0 = b.side(copy.deepcopy(base), venue, {'squad': {'kind': 'reference', 'tier': 'pl-middle'}, 'tactic': {'kind': 'preset', 'style': 'Gegenpress'}})
            s0 = b.side(s0, 1 - venue, {'squad': {'kind': 'reference', 'tier': 'pl-middle'}, 'tactic': {'kind': 'preset', 'style': ns.PANEL[0]}})
            league.equalise(s0); s0 = A.validate_scenario(s0); team0 = s0['teams'][venue]
            slot = {i: rnd.GROUP_OF[ns.position_group(ip)] for i, ip, _ in ns.starters(team0)}
            for cname, edit in g['conds']:
                if not callable(edit): continue
                s = copy.deepcopy(s0); edit(A, s, venue); s = A.validate_scenario(s)
                changes, other = {}, []
                if ns.team_diff(s0['teams'][1 - venue], s['teams'][1 - venue]): other.append('opponent')
                for (i, fld), (x, y) in ns.team_diff(team0, s['teams'][venue]).items():
                    if i is None: other.append(fld); continue
                    key = ('a', int(fld[4:])) if fld.startswith('attr') else ('p', fld)
                    label = by_key.get(key)
                    if label is None: other.append(f'{fld}'); continue
                    if i not in slot: other.append('substitutes'); continue
                    step = (y - x) / 5 if key[0] == 'a' else (y - x)
                    gk = slot[i]
                    changes.setdefault(f'{gk}|{label}', 0); changes[f'{gk}|{label}'] += step
                result[f'{name}|{g["name"]}|{cname}'] = {'study': name, 'group': g['name'], 'cond': cname, 'changes': changes,
                                                          'other': sorted(set(other))}
        print('designs', name, flush=True)
    (out / 'designs.json').write_text(json.dumps(result, indent=1)); print(len(result), 'conditions')


def predict(a):
    import neutral_study as ns
    out = Path(a.out); D = json.loads((out / 'designs.json').read_text())
    R = json.loads((Path(a.random) / 'analysis.json').read_text()); cols = ['|'.join(c) for c in R['cols']]
    idx = {c: i for i, c in enumerate(cols)}
    rows = []; cache = {}
    for key, d in D.items():
        if not d['changes'] or any(o not in ('substitutes',) for o in d['other']): continue
        if d['study'] not in cache: cache[d['study']] = ns.load(ROOT / 'runs/roadmap' / d['study'])
        data = cache[d['study']]
        r = {'key': key, 'study': d['study'], 'cond': d['cond'], 'subs': 'substitutes' in d['other'],
             'levels': sum(abs(v) for v in d['changes'].values())}
        for m in MEASURES:
            x = R['measures']['Pts' if m == 'pts' else m]; p = sum(x['b'][idx[c]] * v for c, v in d['changes'].items() if c in idx)
            sp = math.sqrt(sum((x['se'][idx[c]] * v) ** 2 for c, v in d['changes'].items() if c in idx))
            e = ns.effect(data, d['group'], d['cond'], m)
            r[m] = {'pred': p, 'pred_se': sp, 'meas': e[0], 'meas_se': e[2], 'n': e[3]}
        if r['xPts']['n'] >= 10: rows.append(r)
    L = ['# Study 13b\'s model against the roadmap studies', '',
         f"{len(rows)} conditions measured one at a time in Studies {', '.join(sorted({r['study'] for r in rows}))}, in Study 13b's set-up "
         '(Gegenpress, Premier League middle-eight squads, familiarity 80). Predicted: the random-configuration model (linear, '
         'additive, per level and position); measured: paired against each study\'s unchanged side. Per game.', '']
    for m in ('xPts', 'xGD', 'pts', 'GA'):
        z = [(r[m]['meas'] - r[m]['pred']) / math.hypot(r[m]['meas_se'], r[m]['pred_se']) for r in rows]
        sw = sum(r[m]['pred'] * r[m]['meas'] / r[m]['meas_se'] ** 2 for r in rows); sp = sum(r[m]['pred'] ** 2 / r[m]['meas_se'] ** 2 for r in rows)
        xs = [r[m]['pred'] for r in rows]; ys = [r[m]['meas'] for r in rows]; mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        cor = sum((p - mx) * (q - my) for p, q in zip(xs, ys)) / math.sqrt(sum((p - mx) ** 2 for p in xs) * sum((q - my) ** 2 for q in ys))
        from random_study import chi2_sf
        q = sum(v * v for v in z)
        L.append(f"- **{m}:** measured = {sw / sp:.2f} × predicted (weighted; 1 = right scale), correlation {cor:.2f}; "
                 f"misfit chi-square {q:.0f} on {len(z)} (p {chi2_sf(q, len(z)):.3f}); |z| > 3 for {sum(abs(v) > 3 for v in z)}.")
    L += ['', '## By study (xPts)', '', '| Study | Conditions | Slope | Misfit chi-square | Largest miss (z) |', '|---|---|---|---|---|']
    for st in sorted({r['study'] for r in rows}):
        rs_ = [r for r in rows if r['study'] == st]
        z = [(r['xPts']['meas'] - r['xPts']['pred']) / math.hypot(r['xPts']['meas_se'], r['xPts']['pred_se']) for r in rs_]
        sw = sum(r['xPts']['pred'] * r['xPts']['meas'] / r['xPts']['meas_se'] ** 2 for r in rs_)
        sp = sum(r['xPts']['pred'] ** 2 / r['xPts']['meas_se'] ** 2 for r in rs_)
        i = max(range(len(z)), key=lambda i: abs(z[i]))
        L.append(f"| {st} | {len(rs_)} | {sw / sp if sp else float('nan'):.2f} | {sum(v * v for v in z):.0f} on {len(z)} | {rs_[i]['cond']} ({z[i]:+.1f}) |")
    L += ['', '## Every condition', '', '| Study | Condition | Levels changed | xPts predicted | xPts measured | z | Goals against predicted | measured |',
          '|---|---|---|---|---|---|---|---|']
    for r in sorted(rows, key=lambda r: (r['study'], r['cond'])):
        z = (r['xPts']['meas'] - r['xPts']['pred']) / math.hypot(r['xPts']['meas_se'], r['xPts']['pred_se'])
        L.append(f"| {r['study']} | {r['cond']}{' (+subs)' if r['subs'] else ''} | {r['levels']:.0f} | {r['xPts']['pred']:+.3f} ± {r['xPts']['pred_se']:.3f} | "
                 f"{r['xPts']['meas']:+.3f} ± {r['xPts']['meas_se']:.3f} | {z:+.1f} | {r['GA']['pred']:+.3f} | {r['GA']['meas']:+.3f} |")
    (out / 'predict.json').write_text(json.dumps(rows)); text = '\n'.join(L) + '\n'; (out / 'predict.md').write_text(text); print(text)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    d = sub.add_parser('designs'); d.add_argument('out')
    q = sub.add_parser('predict'); q.add_argument('out'); q.add_argument('--random', default=str(ROOT / 'runs/random/gegenpress'))
    a = p.parse_args(); {'designs': designs, 'predict': predict}[a.cmd](a)


if __name__ == '__main__':
    main()
