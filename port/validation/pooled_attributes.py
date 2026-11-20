"""Attribute evidence across studies: does the random-configuration model (Study 13b) predict the conditions measured
one at a time in the roadmap studies, and what do all studies say together?

  python port/validation/pooled_attributes.py designs OUT              # each roadmap condition's changes, per starter
  python port/validation/pooled_attributes.py predict OUT [--random runs/random/gegenpress]   # OUT/predict.md
  python port/validation/pooled_attributes.py minutes OUT [--from runs/roadmap/13] [--workers 7]   # OUT/minutes/
  python port/validation/pooled_attributes.py pool OUT [--random runs/random/gegenpress]      # OUT/pool.md, pool.json

'designs' rebuilds every roadmap condition played in Study 13b's set-up (Gegenpress, the Premier League middle-eight
squad on both sides, familiarity 80, the default templates and opponents) on one setting and records what it changes:
levels per starter and field, plus anything the random study did not vary (subs, the opponent, position ratings,
morale, Current Ability), which marks the condition as out of the model's scope or only partly in it.

'predict' compares each condition's measured effect (paired against its study's unchanged side, as reported) with the
random model's prediction: the sum over starters and fields of the per-level coefficient for that position and field
times the change in levels. A linear, additive model predicts every condition; where it misses shows thresholds,
diminishing returns or combinations.

'minutes' replays the unchanged matches of a roadmap study (Study 13 by default) and records every substitution of the
tested side: who comes on, when, in which lineup slot. A substitute's change of one level is then worth the
coefficient of the position it plays, times its minutes there over a starter's minutes in that position.

'pool' combines everything in one estimate per position and attribute: Study 13b's coefficients are the starting
point (with their standard errors), and every roadmap condition within the range that study measured (changes of at
most 5 levels, nothing in CURVED) adds its measured effect, substitutes credited by their minutes. Conditions of the
same study group share one baseline, so their errors are correlated (each carries the baseline's luck): with every
match on a seed equally alike, two conditions' covariance is half of each one's variance. The fit uses that rather
than a free offset per study. Checked by leaving one study out at a time and predicting it.
"""
import argparse, copy, json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for p in ('scripts', 'src', 'port/validation'): sys.path.insert(0, str(ROOT / p))

STUDIES = ['09b', '10', '11', '12', '13', '14', '14b', '20', '21', '21b']
CURVED = ('Jumping Reach',)   # convex (random_curvature.py): a one-sided +5 gains more than the average slope
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
            (out / 'lineup.json').write_text(json.dumps([[i, rnd.GROUP_OF[ns.position_group(ip)]] for i, ip, _ in ns.starters(team0)]))
            for cname, edit in g['conds']:
                if not callable(edit): continue
                s = copy.deepcopy(s0); edit(A, s, venue); s = A.validate_scenario(s)
                changes, subs, other, steps, lows = {}, {}, [], [0], [20]
                if ns.team_diff(s0['teams'][1 - venue], s['teams'][1 - venue]): other.append('opponent')
                for (i, fld), (x, y) in ns.team_diff(team0, s['teams'][venue]).items():
                    if i is None: other.append(fld); continue
                    key = ('a', int(fld[4:])) if fld.startswith('attr') else ('p', fld)
                    label = by_key.get(key)
                    if label is None: other.append(f'{fld}'); continue
                    step = (y - x) / 5 if key[0] == 'a' else (y - x)
                    steps.append(abs(step))
                    if key[0] == 'a': lows.append(min(x, y) / 5)
                    if i not in slot:   # a substitute: credited by the minutes it plays in each position ('minutes')
                        other.append('substitutes'); subs[f'{i}|{label}'] = subs.get(f'{i}|{label}', 0) + step; continue
                    gk = slot[i]
                    changes.setdefault(f'{gk}|{label}', 0); changes[f'{gk}|{label}'] += step
                result[f'{name}|{g["name"]}|{cname}'] = {'study': name, 'group': g['name'], 'cond': cname, 'changes': changes,
                                                          'subs': subs, 'max_step': max(steps), 'min_level': min(lows), 'other': sorted(set(other))}
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


def minutes(a):
    import overnight
    out = (Path(a.out) / 'minutes').resolve(); out.mkdir(parents=True, exist_ok=True)
    if not (out / 'jobs.json').exists():
        jobs = [j for j in json.loads((Path(a.source) / 'jobs_all.json').read_text()) if j[1].split('|')[1] == 'none']
        (out / 'jobs.json').write_text(json.dumps(jobs))
    overnight.run(out, a.workers); W = sub_weights(Path(a.out)); print(json.dumps(W, indent=1))


def sub_weights(out):
    """{bench player: {position: weight}}: minutes it plays in the position over a starter's minutes there (per match)."""
    lineup = json.loads((out / 'lineup.json').read_text()); group = [g for _, g in lineup]
    played, n = {}, 0
    for line in open(out / 'minutes' / 'results.jsonl'):
        r = json.loads(line); me = int(r['cond'].split('|')[3]); T = r.get('end') or 96.0; n += 1
        since = {i: (0.0, group[k]) for k, (i, _) in enumerate(lineup)}
        def add(i, until):
            t0, g = since.pop(i); played.setdefault(i, {}).setdefault(g, 0.0); played[i][g] += until - t0
        for side, t, off, on, slot in r['subs']:
            if side != me or off not in since: continue
            add(off, t); since[on] = (t, group[slot])
        for i in list(since): add(i, T)
    starters = {i for i, _ in lineup}; per = {}
    for i, g in lineup: per.setdefault(g, []).append(sum(played.get(i, {}).values()) / n)
    base = {g: sum(v) / len(v) for g, v in per.items()}
    W = {str(i): {g: m / n / base[g] for g, m in d.items()} for i, d in played.items() if i not in starters}
    return {'matches': n, 'starter_minutes': base, 'bench_minutes': {str(i): sum(d.values()) / n for i, d in played.items() if i not in starters}, 'weights': W}


def pool(a):
    import numpy as np, neutral_study as ns
    from random_study import chi2_sf
    out = Path(a.out); D = json.loads((out / 'designs.json').read_text()); SW = sub_weights(out); W = SW['weights']
    R = json.loads((Path(a.random) / 'analysis.json').read_text()); cols = ['|'.join(c) for c in R['cols']]; idx = {c: i for i, c in enumerate(cols)}
    P = len(cols); cache = {}; conds = []
    for key, d in D.items():
        if not (d['changes'] or d['subs']) or any(o != 'substitutes' for o in d['other']): continue
        x0, x1 = np.zeros(P), np.zeros(P)   # x0: starters only; x1: with substitutes by minutes
        for c, v in d['changes'].items():
            if c in idx: x0[idx[c]] += v; x1[idx[c]] += v
        for c, v in d['subs'].items():
            i, label = c.split('|', 1)
            for g, w in W.get(i, {}).items():
                if f'{g}|{label}' in idx: x1[idx[f'{g}|{label}']] += w * v
        if d['study'] not in cache: cache[d['study']] = ns.load(ROOT / 'runs/roadmap' / d['study'])
        data = cache[d['study']]; dd, bb = data.get((d['group'], d['cond']), {}), data.get((d['group'], 'none'), {})
        keys = set(dd) & set(bb)
        if len(keys) < 10: continue
        conds.append({'key': key, 'study': d['study'], 'group': d['group'], 'cond': d['cond'], 'x0': x0, 'x1': x1, 'keys': keys,
                      'in_range': d['max_step'] <= 5 and not any(c.split('|', 1)[1] in CURVED for c in list(d['changes']) + list(d['subs'])), 'subs': bool(d['subs']), 'data': (dd, bb)})
    result, L = {}, ['# Pooled attribute estimates: Study 13b with every roadmap condition', '']
    L += [f"Substitutes' minutes from {SW['matches']} unchanged matches of Study 13 (tested side): " +
          ', '.join(f"bench player {i}: {m:.0f} min" for i, m in sorted(SW['bench_minutes'].items(), key=lambda x: -x[1]) if m >= 0.5) +
          '; starters: ' + ', '.join(f'{g} {m:.0f}' for g, m in SW['starter_minutes'].items()) + ' min.', '']
    for m in ('xPts', 'xGD', 'GA', 'GF', 'xGF', 'xGA', 'pts'):
        x = R['measures']['Pts' if m == 'pts' else m]; b0 = np.array(x['b']); s0 = np.array(x['se'])
        y = []; V = None
        for c in conds:
            dd, bb = c['data']; v = [dd[k][m] - bb[k][m] for k in c['keys']]; y.append(sum(v) / len(v))
            c['var'] = np.var(v, ddof=1) / len(v)
        y = np.array(y); n = len(conds); V = np.zeros((n, n))
        for i, c in enumerate(conds):
            V[i, i] = c['var']
            for j in range(i):
                e = conds[j]
                if (c['study'], c['group']) != (e['study'], e['group']): continue
                # same seeds, every match equally correlated: cov = half of each variance (whatever the correlation)
                common = len(c['keys'] & e['keys'])
                V[i, j] = V[j, i] = 0.5 * math.sqrt(c['var'] * e['var'] * len(c['keys']) * len(e['keys'])) * common / (len(c['keys']) * len(e['keys']))
        inr = np.array([c['in_range'] for c in conds])
        def fit(use, X):
            Xu, Vi = X[use], np.linalg.inv(V[np.ix_(use, use)])
            Pm = np.diag(1 / s0 ** 2) + Xu.T @ Vi @ Xu; C = np.linalg.inv(Pm)
            return C @ (b0 / s0 ** 2 + Xu.T @ Vi @ y[use]), C
        def check(sel, X, b, C):   # chi-square and slope of measured on predicted for the selected conditions
            r = y[sel] - X[sel] @ b; S = V[np.ix_(sel, sel)] + X[sel] @ C @ X[sel].T; Si = np.linalg.inv(S); p = X[sel] @ b
            return float(r @ Si @ r), int(sel.sum()), float((p @ Si @ y[sel]) / (p @ Si @ p)), float(1 / math.sqrt(p @ Si @ p))
        X0 = np.array([c['x0'] for c in conds]); X1 = np.array([c['x1'] for c in conds]); C0 = np.diag(s0 ** 2)
        b, C = fit(inr, X1); se = np.sqrt(np.diag(C))
        studies = sorted({c['study'] for c in conds}); loo = {}
        for st in studies:
            sel = inr & np.array([c['study'] == st for c in conds])
            if not sel.any(): continue
            bl, Cl = fit(inr & ~sel, X1); loo[st] = check(sel, X1, bl, Cl) + check(sel, X1, b0, C0)
        squad = inr & np.array([c['subs'] for c in conds])
        result[m] = {'b': b.tolist(), 'se': se.tolist(), 'random_b': b0.tolist(), 'random_se': s0.tolist(),
                     'prior_check': {'starters_only': check(inr, X0, b0, C0), 'with_subs': check(inr, X1, b0, C0),
                                     'squad_starters_only': check(squad, X0, b0, C0), 'squad_with_subs': check(squad, X1, b0, C0),
                                     'out_of_range': check(~inr, X1, b, C)}, 'leave_one_out': loo}
        if m not in ('xPts', 'GA'): continue
        pc = result[m]['prior_check']; f = lambda t: f'chi-square {t[0]:.0f} on {t[1]} (p {chi2_sf(t[0], t[1]):.3f}), slope {t[2]:.2f} ± {t[3]:.2f}'
        L += [f'## {m}', '', f"{int(inr.sum())} conditions in range ({sum(c['subs'] for c, i in zip(conds, inr) if i)} also change substitutes), "
              f"{int((~inr).sum())} outside it. Study 13b's model, before pooling:", '',
              f"- every condition in range, starters only: {f(pc['starters_only'])}",
              f"- the same with substitutes credited by minutes: {f(pc['with_subs'])}",
              f"- conditions that change substitutes, starters only: {f(pc['squad_starters_only'])}",
              f"- the same with substitutes: {f(pc['squad_with_subs'])}",
              f"- outside the range, against the pooled model: {f(pc['out_of_range'])}", '',
              '**Leave one study out** (pooled from the others, then predicting it; Study 13b alone in brackets):', '',
              '| Study | Conditions | Chi-square | Slope | Study 13b alone: chi-square | slope |', '|---|---|---|---|---|---|']
        for st, t in loo.items():
            L.append(f'| {st} | {t[1]} | {t[0]:.0f} (p {chi2_sf(t[0], t[1]):.2f}) | {t[2]:.2f} ± {t[3]:.2f} | {t[4]:.0f} | {t[6]:.2f} ± {t[7]:.2f} |')
        lineup = json.loads((out / 'lineup.json').read_text()); count = {}
        for _, g in lineup: count[g] = count.get(g, 0) + 1
        labels = sorted({c.split('|', 1)[1] for c in cols})
        L += ['', '**Whole team, one level for every starter** (per season; what the earlier studies mostly measured):', '',
              '| Attribute | Study 13b | Pooled | Standard error ratio |', '|---|---|---|---|']
        team = []
        for lab in labels:
            w = np.zeros(P)
            for g, k in count.items():
                if f'{g}|{lab}' in idx: w[idx[f'{g}|{lab}']] = k
            team.append((lab, w @ b0, math.sqrt(w @ C0 @ w), w @ b, math.sqrt(w @ C @ w)))
        for lab, p0, q0, p1, q1 in sorted(team, key=lambda t: t[4] / t[2]):
            L.append(f'| {lab} | {38 * p0:+.2f} ± {38 * q0:.2f} | {38 * p1:+.2f} ± {38 * q1:.2f} | {q1 / q0:.2f} |')
        result[m]['team'] = {t[0]: {'random': t[1:3], 'pooled': t[3:5]} for t in team}
        gain = sorted(range(P), key=lambda i: se[i] / s0[i])
        L += ['', f'**Where pooling adds most** (per season, ×38; standard error after over before):', '',
              '| Position, attribute | Study 13b | Pooled | Standard error ratio |', '|---|---|---|---|']
        for i in gain[:12]:
            L.append(f'| {cols[i]} | {38 * b0[i]:+.3f} ± {38 * s0[i]:.3f} | {38 * b[i]:+.3f} ± {38 * se[i]:.3f} | {se[i] / s0[i]:.2f} |')
        L.append(f"\nStandard errors shrink by at least 10% for {sum(se / s0 < 0.9)} of {P} estimates, by at least 30% for {sum(se / s0 < 0.7)}.")
        L.append('')
    (out / 'pool.json').write_text(json.dumps({'cols': cols, 'sub_weights': SW, 'measures': result}))
    text = '\n'.join(L) + '\n'; (out / 'pool.md').write_text(text); print(text)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    d = sub.add_parser('designs'); d.add_argument('out')
    q = sub.add_parser('predict'); q.add_argument('out'); q.add_argument('--random', default=str(ROOT / 'runs/random/gegenpress'))
    m = sub.add_parser('minutes'); m.add_argument('out'); m.add_argument('--from', dest='source', default=str(ROOT / 'runs/roadmap/13'))
    m.add_argument('--workers', type=int, default=7)
    o = sub.add_parser('pool'); o.add_argument('out'); o.add_argument('--random', default=str(ROOT / 'runs/random/gegenpress'))
    a = p.parse_args(); {'designs': designs, 'predict': predict, 'minutes': minutes, 'pool': pool}[a.cmd](a)


if __name__ == '__main__':
    main()
