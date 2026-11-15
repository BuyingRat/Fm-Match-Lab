"""Study 13b, no new matches: does an attribute's per-level value depend on the player's starting level (curvature),
and do attributes interact within a player? Usage: python port/validation/random_curvature.py runs/random/gegenpress"""
import sys, json, copy, numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
for p in ('scripts', 'src', 'port/validation'): sys.path.insert(0, str(ROOT / p))
import study, league, neutral_study as ns, random_study as rs
out = Path(sys.argv[1]); meta = json.loads((out / 'meta.json').read_text())
A = study.app(); F = rs.fields(); names = [rs.nice(l) for l, _, _ in F]
path = ns.template_path(ns.DEFAULT_TEMPLATES[0]); base = league.same_squad_size(A.validate_scenario(A.SAVED_MATCHES.open(path).default))
b = league.Builder(A, ROOT / 'runs/pooled/scratch')
s0 = b.side(copy.deepcopy(base), 0, {'squad': {'kind': 'reference', 'tier': 'pl-middle'}, 'tactic': {'kind': 'preset', 'style': meta['style']}})
s0 = b.side(s0, 1, {'squad': {'kind': 'reference', 'tier': 'pl-middle'}, 'tactic': {'kind': 'preset', 'style': ns.PANEL[0]}})
league.equalise(s0); s0 = A.validate_scenario(s0); t = s0['teams'][0]
B = np.array([[ (t['players'][i]['attributes'][key] / 5 if kind == 'a' else t['players'][i]['native_profile'][key]) for _, kind, key in F]
              for i, ip, _ in ns.starters(t)])                                # base level per starter and field
d = np.load(out / 'design.npz'); X, S = d['X'].astype(float), d['setting']
res = rs.outcomes(out, meta); idx = np.array(sorted(res)); X, S = X[idx], S[idx]
groups = [x['group'] for x in meta['xi']]; gk_only = set(meta['gk_only'])
cols = [(g, f) for g in rs.GROUPS for f, nm in enumerate(names) if g == 'GK' or nm not in gk_only]
Z = np.stack([X[:, [j for j, gg in enumerate(groups) if gg == g], f].sum(1) for g, f in cols], 1)
outf = [j for j, g in enumerate(groups) if g != 'GK']
TOP = ['Pace', 'Acceleration', 'Jumping Reach', 'Stamina', 'Anticipation', 'Balance', 'Dribbling', 'Concentration', 'Strength']
print('starting levels (outfield):', {n: (int(B[outf, names.index(n)].min()), int(B[outf, names.index(n)].max())) for n in TOP})
for m in ('xPts', 'GD'):
    y = np.array([res[c][m] for c in idx], float)
    extra, labels = [], []
    for n in TOP:   # curvature: change x (base level - mean), summed over outfield starters
        f = names.index(n); c = B[outf, f] - B[outf, f].mean()
        extra.append((X[:, outf, f] * c).sum(1)); labels.append(f'{n}: slope change per level of starting level')
    for a_, b_ in [('Pace', 'Acceleration'), ('Strength', 'Balance'), ('Pace', 'Dribbling'), ('Anticipation', 'Decisions'),
                   ('Jumping Reach', 'Heading'), ('Finishing', 'Composure'), ('Passing', 'Vision'), ('Acceleration', 'Agility')]:
        fa, fb = names.index(a_), names.index(b_)
        extra.append((X[:, outf, fa] * X[:, outf, fb]).sum(1) / 5); labels.append(f'{a_} x {b_} (same player)')
    bb, se, _ = rs.regress(y, np.hstack([Z, np.stack(extra, 1)]), S, len(meta['settings']))
    print(f'\n{m} (per season, 38 games)')
    for k, l in enumerate(labels):
        i = len(cols) + k
        if 'starting' in l:
            n = l.split(':')[0]; f = names.index(n); main = bb[:len(cols)][[cols.index((g, f)) for g in ('ST', 'AM', 'DM', 'FB', 'CB')]].mean()
            print(f'  {l}: {bb[i]*38:+.4f} (t {bb[i]/se[i]:+.1f}); main effect per level about {main*38:+.3f}')
        else:
            print(f'  {l}: {bb[i]*38:+.4f} per +5 x +5 /5 (t {bb[i]/se[i]:+.1f})')
