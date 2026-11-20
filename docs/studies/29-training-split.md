# Study 29: two ways to split familiarity training, head to head

**Status:** done (16 November, 5,760 matches).

**Question.** Training can't push every tactical area to the top. Is it better to max out the two areas that matter
most (chance creation and pressing intensity) and let the rest fall, or to keep those two a little lower and the rest
higher? And how do both compare with an even split?

**In short:**
- **Spreading wins clearly.** B (the two leading areas at 85-87, four others at 42) beats A (the two at 100, the four
  at 28) by **+0.18 expected points a game in a meeting** (t 7.7), +6.8 ± 1.7 a season, and by +0.30 actual points
  a game (t 5.4).
- **An even split is worst.** C (every area at 42) loses to A by −0.13 (t −5.1) and to B by −0.21 (t −9.1).
- **Pushing the two leading areas from about 85 to 100 gains little; letting the others fall to 28 costs clearly
  more.** Keep the leading areas high, but not at the expense of the rest.

## Scenarios

The values are the area pies on the game's Tactical Effectiveness panel (full pie = 100), set exactly for every
player.

| Area | A | B | C |
|---|---|---|---|
| Chance creation | 100 | 85 | 42 |
| Pressing intensity | 100 | 87 | 42 |
| Out-of-possession shape | 28 | 42 | 42 |
| Passing style | 28 | 42 | 42 |
| Build-up | 28 | 42 | 42 |
| In-possession shape | 28 | 42 | 42 |
| Pressing trap | 0 | 0 | 42 |
| Line of engagement | 0 | 0 | 42 |

## Design

- **Head to head:** in each match one side has one scenario and the other side the other. Every match-up is played
  twice on the same seed with the sides swapped, so home advantage and any difference between the squads cancel. A
  head-to-head edge counts both sides' change, which makes it about 3.5 times as efficient per match as comparing
  each scenario with a common opponent.
- **Settings:** Study 24's neutral ground: the synthetic Premier League middle-eight squad on both sides, the tested
  side in Gegenpress or Control Possession against four preset opponents (Gegenpress, Control Possession, Park the
  Bus, Route One), home and away, two template matches: 32 settings, 30 seeds each.
- **Size:** three pairings (B against A, C against A, C against B), 960 swapped pairs each: 5,760 matches.

## Results

Edge of the second scenario per meeting, averaged over each swapped pair; t in brackets.

| Pairing | Style | Expected points a game | a season | xG difference | Points a game | Wins / draws / losses |
|---|---|---|---|---|---|---|
| B vs A | Gegenpress | +0.183 (5.6) | +7.0 ± 2.4 | +0.170 (5.9) | +0.372 (4.8) | 44% / 25% / 31% |
| | Control Possession | +0.173 (5.2) | +6.6 ± 2.5 | +0.149 (5.4) | +0.228 (2.9) | 38% / 32% / 30% |
| | **both** | **+0.178 (7.7)** | **+6.8 ± 1.7** | +0.159 (8.0) | +0.300 (5.4) | 41% / 28% / 31% |
| C vs A | Gegenpress | −0.081 (−2.3) | −3.1 ± 2.6 | −0.072 (−2.3) | +0.106 (1.3) | 39% / 25% / 36% |
| | Control Possession | −0.177 (−5.0) | −6.7 ± 2.6 | −0.139 (−4.7) | −0.047 (−0.6) | 36% / 27% / 37% |
| | **both** | **−0.129 (−5.1)** | **−4.9 ± 1.9** | −0.105 (−4.9) | +0.030 (0.5) | 37% / 26% / 36% |
| C vs B | Gegenpress | −0.283 (−8.5) | −10.8 ± 2.5 | −0.244 (−8.6) | −0.175 (−2.2) | 34% / 27% / 39% |
| | Control Possession | −0.137 (−4.3) | −5.2 ± 2.4 | −0.112 (−4.2) | −0.084 (−1.0) | 34% / 29% / 37% |
| | **both** | **−0.210 (−9.1)** | **−8.0 ± 1.7** | −0.178 (−9.0) | −0.130 (−2.3) | 34% / 28% / 38% |

- **The order is B, then A, then C in both styles.**
- **C against A in actual points** is level (+0.03), although A is clearly ahead in expected points: actual points are
  noisier, and the expected-points result is the more reliable.

## Against Study 25's prediction

Study 25 measured each area's value at every level against a fixed opponent. Adding up its values for each scenario
predicts the same order (B > A > C). A head-to-head edge should be about twice a gap against a common opponent, which
gives predicted edges of about 2.4-3.8 points a season for B over A, 4.4-7 for A over C and 8.4-9.6 for B over C.
A over C and B over C fit. **B's edge over A is about twice the prediction** (the difference has t about 2).

A possible reason: Study 25 varied the opponent's areas only all together, so it can't show whether an area kept low
costs more against an opponent strong in the matching area, as happens in a meeting between A and B. This is a lead,
not a finding.

## What this means

- **Don't max two areas and neglect the rest.** Above about 85 the two leading areas gain little; below about 40 the
  other areas start to cost.
- **But don't spread evenly either.** Chance creation and pressing intensity are worth far more than the other areas
  (Study 25), so an even split leaves points on the table.
- **A good target:** chance creation and pressing intensity at 85 or above, out-of-possession shape and the build-up
  areas at least in the 40s.

## Caveats

- **One squad and two styles,** every player at the same values.
- **Three scenarios.** This doesn't find the best split, only which of these is better; a training guide needs a
  separate analysis of how training time turns into area values.

## Reproduce

```sh
.venv/bin/python port/validation/study29_training_split.py build runs/study29b --from runs/study24 --seeds 30 --contexts pies --h2h
.venv/bin/python port/validation/study29_training_split.py run runs/study29b --workers 7   # about 1.5 hours
.venv/bin/python port/validation/study29_training_split.py report runs/study29b
```
