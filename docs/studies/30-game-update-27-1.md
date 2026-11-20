# Study 30: what the 27.1 update changed in the match engine

**Status:** done (20 November, 1,500 matches).

**Question.** FM27 27.1 (18 November) shipped a new match engine. How do matches play differently from 27.0.1, and
are results from earlier studies still valid?

**In short:**
- **Matches are a little scrappier.** Pass completion fell by 0.8 percentage points (t −7.2). There are 1.6 more
  shots a match (t 3.3), mostly the opponent's, but each is slightly worse, so total xG is unchanged. Cards rose by
  0.4 a match (t 2.3, borderline).
- **Results barely moved.** The team's points fell by 0.12 a game (t −1.2), within the noise.
- **The old engine is still in the game.** Every change in 27.1 is behind a version switch. Set to 27.0.1's version,
  the 27.1 engine replays all 300 test matches exactly as 27.0.1 did, so earlier results stay valid and can be
  reproduced on the new version.

## Design

- **Matches:** ten saved matches of the team, 30 seeds each (300 matches per condition), unchanged, with live
  in-match management as in the [common design](README.md#common-design).
- **Conditions:** 27.0.1 (from earlier studies), and 27.1 with its changes switched on in three steps, by setting
  the engine version the match runs at (`FM27_MAC_ENGINE_VERSION`, see [RESEARCH.md](../RESEARCH.md)): none, the
  first group, the first two groups, all.
- **Comparison:** the two engines can't be paired match by match (any change alters a match from the first touch),
  so conditions are compared as averages over the same 300 matches and seeds; t in brackets.

## Results

Per match, both teams together unless stated.

| | 27.0.1 | 27.1 | Change |
|---|---|---|---|
| Pass completion | 86.6% | 85.8% | −0.8 points (−7.2) |
| Shots | 27.3 | 28.8 | +1.6 (+3.3) |
| Opponent's shots | 11.0 | 12.4 | +1.4 (+4.4) |
| xG per shot | 0.127 | 0.122 | −0.005 (−2.3) |
| Total xG | 3.45 | 3.49 | +0.04 (+0.5) |
| Goals | 3.36 | 3.53 | +0.17 (+1.1) |
| Cards | 4.6 | 5.0 | +0.4 (+2.3) |
| Team's points a game | 1.97 | 1.85 | −0.12 (−1.2) |

Pass completion fell in all ten matches and for both teams; the opponent shot more in nine of ten.

**Check:** the 27.1 engine at 27.0.1's version gave the same 300 matches as 27.0.1, goal for goal; at its own
version it gave the same 300 as an earlier 27.1 run.

## Where the changes come from

The update holds about 50 separate changes in three groups. Each step below is measured against the one before.

| Group | What it touches | Effect |
|---|---|---|
| First | positioning, how players value on-ball and passing options, marking, perception, restarts, injuries | pass completion −1.0 points (−8.1), +0.9 shots (+2.0), +0.18 xG (+2.1) |
| Second | going into challenges, contested balls in the air, how passes are struck, reaction to pressure, running speed, man-marking | pass completion +0.7 points (+5.4), −1.7 shots (−3.7), cards +0.4 (+2.4) |
| Third | first contact with the ball, how far out players shoot, jump timing, the random rolls, team shape | +2.4 shots (+5.0), xG per shot −0.009 (−3.4), pass completion −0.6 points (−4.5) |

The groups partly cancel: the first lowers passing accuracy and the second gives some back; the extra low-quality
shots come mostly from the third, the extra cards from the second.

## What this means

- **Earlier studies (1-29, run on 27.0.1) stand.** Their numbers describe 27.0.1; a study that needs to compare with
  them can run on 27.1 at 27.0.1's version.
- **New studies run on the 27.1 engine** by default. With pass accuracy and shot selection changed, effects of
  passing and shooting attributes, traits such as Shoots From Distance and tactics built on short passing may shift
  a little; check before relying on an old number for those.

## Caveats

- One team's matches, mostly Premier League; the effects are small, so other clubs could differ in size.
- The groups were switched on in order, so a group's effect is measured with the earlier groups already on.

## Reproduce

```sh
FM27_MAC_ENGINE_VERSION=<word> .venv/bin/python scripts/study.py run runs/<study>   # one version per run
```

The version words are in [MACOS.md](../MACOS.md) (one per game version); the intermediate steps used here are not
published.
