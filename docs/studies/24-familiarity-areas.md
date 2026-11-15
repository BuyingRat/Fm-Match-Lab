# Study 24: which tactical familiarity areas are worth training?

**Status:** done (15 November; 13,600 matches one area at a time, then 27,200 in Study 24b with every area at a
random level). FM27 splits tactical familiarity into eight areas, and training can focus on some of them. Which areas
matter? Does the answer depend on the style?

**In short (Study 24b, the precise run):**
- **Two areas matter most, in both styles: chance creation and pressing intensity.** Letting either fall from 50 to
  20 costs about 0.07-0.08 expected points per game (t −5.6 to −7.2), about 3 points a season, at both ends: fewer
  chances created and more conceded.
- **Out-of-possession shape comes third** (−0.02 to −0.03 per game, t −2.0 to −2.6); passing style and build-up are
  smaller still. Line of engagement, pressing trap and in-possession shape show nothing.
- **Raising an area above 50 gains nothing measurable** in either style (all sixteen |t| < 2; "all equal" p 0.45-0.54).
  Familiarity is a floor to keep, not a ceiling to push.
- **The styles agree** (p 0.27 for the eight swings, p 0.98 for the losses). Study 24's "Control Possession shows no
  area" was a lack of precision.
- **What the engine does explains it.** Each area strengthens two of every player's attributes during play; the two
  areas that matter most are the two tied to Anticipation, the attribute with the most value of its own. The boost is
  limited, and a reasonably trained area already gets most of it: neglecting an area takes the boost away, while
  pushing it higher adds little. A prediction built on this fits the measured losses (correlation 0.94-0.96).

## Design

- **Neutral ground,** as in the other roadmap studies: the synthetic Premier League middle-eight squad on both sides,
  four preset opponents (Gegenpress, Control Possession, Park the Bus, Route One) home and away, two template matches
  between other clubs.
- **Two styles for the tested side:** Gegenpress and Control Possession.
- **Baseline:** every area of every player on both sides held at 50 (the area's training, match-exposure and third
  byte in the effectiveness record).
- **Conditions:** one area of the tested side raised to 80, or lowered to 20, the other seven at 50: sixteen per
  style.
- **Paired:** 50 seeds, giving 400 pairs per condition, each against the baseline on the same matches.

## What the levels mean

The levels are the bytes of each area in the players' effectiveness record (training, match exposure and a third
byte), not the familiarity bar shown in the game. The engine combines them with the player's tactical ability and the
tactic's complexity into an area value of 0-100 (`port/map/exec_record.py`; Study 3). Read from the players' records in
these matches:

| Bytes held at | Area value |
|---|---|
| 50 (baseline) | 73-79 |
| 80 | 100 (the cap) |
| 20 | 46-52 |

So the baseline is already a well-understood tactic; 20 is a clearly neglected area, 80 a fully learned one.

**What an area does in the match.** Read from the engine (without the formulas): during play, each area strengthens
two of every player's attributes, mostly mental ones, when he reads the game, decides or contests the ball. The
stronger the area, the bigger the boost, up to a limit; around the baseline most players already get close to that
limit.

| Area | Attributes it strengthens |
|---|---|
| In-possession shape | First Touch, and the team's cohesion |
| Passing style | Decisions, Composure |
| Build-up | Technique, Vision |
| Chance creation | Anticipation, Off the Ball |
| Out-of-possession shape | Concentration, Marking |
| Line of engagement | Work Rate, Aggression |
| Pressing intensity | Anticipation, Tackling |
| Pressing trap | Decisions, Positioning |

Familiarity never touches the physical attributes (Pace, Acceleration, Jumping Reach, Stamina).

## Study 24b: every area at a random level

Study 24 changed one area at a time and its effects were leads (t 2-3). Pairing on seeds turned out to give no
precision (a changed area makes the same seed's match no more alike than another match), so Study 24b varies all
eight areas at once:

- **Design:** in each match every area of the tested side is 20, 50 or 80 at random (independently); 850 random
  configurations per style, each played on all sixteen settings of Study 24 (four opponents, home and away, two
  templates), the opponent's areas at 50. 27,200 matches. A regression per style gives each area's effect of lowering
  (20 against 50) and raising (80 against 50) from every match, with a constant per setting.
- **Checks:** a 320-match pilot; on made-up results with known effects the regression recovered them (−0.105 for a
  true −0.10). Each effect is measured to about ±0.011 xPts per game, five times more precisely than in Study 24.

Expected points per game; t in brackets.

| Area | Gegenpress: lower to 20 | raise to 80 | Control Possession: lower to 20 | raise to 80 |
|---|---|---|---|---|
| Chance creation | **−0.079 (−6.9)** | +0.021 (+1.9) | **−0.082 (−7.2)** | +0.011 (+1.0) |
| Pressing intensity | **−0.081 (−6.9)** | +0.019 (+1.7) | **−0.066 (−5.6)** | +0.005 (+0.4) |
| Out-of-possession shape | −0.024 (−2.0) | +0.001 (+0.1) | −0.029 (−2.6) | +0.017 (+1.5) |
| Passing style | −0.023 (−2.0) | −0.002 (−0.1) | −0.022 (−1.9) | +0.004 (+0.4) |
| Build-up | −0.019 (−1.6) | +0.005 (+0.5) | −0.012 (−1.1) | −0.012 (−1.0) |
| In-possession shape | −0.015 (−1.3) | −0.010 (−0.9) | −0.008 (−0.7) | −0.017 (−1.5) |
| Pressing trap | −0.004 (−0.3) | +0.005 (+0.5) | +0.006 (+0.6) | −0.003 (−0.2) |
| Line of engagement | +0.002 (+0.2) | +0.005 (+0.4) | +0.009 (+0.8) | +0.004 (+0.3) |

- **Losses differ between areas** (chi-square 54-58 on 7 degrees of freedom, p < 0.0001 in both styles); **gains don't**
  (p 0.45-0.54, all near zero).
- **Both ends of the pitch:** between 20 and 80, chance creation and pressing intensity each move xG for by +0.06 to
  +0.09 and xG against by −0.06 to −0.10 per game (t 4-8).
- **The styles agree:** the eight losses are the same within noise (chi-square 2.0 on 8, p 0.98); the swings too
  (p 0.27).
- **Study 24 holds up for Gegenpress** (the same two leaders; out-of-possession shape smaller than its one-at-a-time
  −0.08), and **is corrected for Control Possession**, where the same two areas matter as much.

## Study 24: one area at a time (the first run)

Expected points (xPts) per game against the baseline; t in brackets (|t| ≥ 4 established, 3-4 likely). Swing is the
area at 80 minus the same area at 20, on the same matches.

### Gegenpress

| Area | At 80 | At 20 | Swing | xG for at 20 | xG against at 20 |
|---|---|---|---|---|---|
| Chance creation | +0.01 (+0.2) | **−0.10 (−2.8)** | **+0.11 (+2.9)** | −0.10 | +0.06 |
| Pressing intensity | +0.02 (+0.6) | **−0.09 (−2.3)** | **+0.11 (+2.7)** | −0.10 | +0.05 |
| Out-of-possession shape | +0.00 (+0.1) | **−0.08 (−2.2)** | **+0.09 (+2.3)** | −0.09 | +0.06 |
| In-possession shape | +0.00 (+0.0) | −0.03 (−0.8) | +0.03 (+0.8) | −0.09 | −0.03 |
| Build-up | −0.04 (−1.2) | −0.05 (−1.3) | +0.01 (+0.3) | −0.09 | −0.00 |
| Passing style | −0.01 (−0.2) | −0.02 (−0.5) | +0.01 (+0.2) | −0.05 | −0.02 |
| Pressing trap | +0.01 (+0.4) | +0.01 (+0.3) | +0.00 (+0.1) | −0.03 | −0.04 |
| Line of engagement | −0.05 (−1.3) | +0.01 (+0.4) | −0.06 (−1.6) | −0.02 | −0.05 |

Baseline: 1.62 xPts, 1.59 xG for and 1.22 against per game. The areas differ beyond chance: chi-square 17.2 on 7
degrees of freedom (p 0.016) in xPts, 18.3 (p 0.011) in xG difference.

- **The three leaders cost at both ends when neglected:** about 0.10 xG fewer chances created and 0.05-0.06 more
  conceded. Pressing intensity's swing in xG difference is +0.20 (t 3.0).
- **Line of engagement goes the other way** (higher is slightly worse; t −1.6, not significant).

### Control Possession

| Area | At 80 | At 20 | Swing |
|---|---|---|---|
| Chance creation | −0.01 (−0.1) | −0.06 (−1.6) | +0.05 (+1.4) |
| Passing style | +0.03 (+0.7) | −0.03 (−0.7) | +0.05 (+1.3) |
| Build-up | −0.02 (−0.5) | −0.06 (−1.5) | +0.04 (+1.0) |
| Line of engagement | +0.02 (+0.4) | −0.02 (−0.5) | +0.04 (+1.0) |
| Pressing intensity | −0.02 (−0.5) | −0.05 (−1.2) | +0.03 (+0.7) |
| In-possession shape | +0.01 (+0.2) | −0.01 (−0.1) | +0.01 (+0.4) |
| Out-of-possession shape | +0.00 (+0.1) | −0.01 (−0.2) | +0.01 (+0.3) |
| Pressing trap | +0.00 (+0.1) | −0.00 (−0.0) | +0.00 (+0.1) |

Baseline: 1.54 xPts, 1.47 xG for and 1.25 against. The areas don't differ (chi-square 1.6 on 7, p 0.98); the average
swing is +0.03 xPts.

### Do the styles differ?

- **Not detectably:** the eight swings differ between the styles by chi-square 9.2 on 8 degrees of freedom (p 0.32)
  in xPts and 10.0 (p 0.27) in xG difference; the rank correlation of the two orders is 0.21.
- **But the pattern is different in kind:** Gegenpress has three areas that matter and five that don't; Control
  Possession has eight small, similar effects. The largest single difference is Out-of-possession shape (Gegenpress
  −0.08 at 20, Control Possession −0.01; z −1.4) and Line of engagement in the swing (z −1.8).
- **Chance creation is first in both orders.**

## Why: what each area strengthens

If an area matters because of the attributes it strengthens, its effect should follow those attributes' value. Before
the results were in, each area's effect was predicted from the two attributes it strengthens (their value per level
from Study 13b, Gegenpress, for the ten outfield players), how much of a boost each level of the area gives them, and
the limit on that boost. The prediction treats the boost as worth what the attribute is worth everywhere it is used,
so it is an upper bound. Measured: Study 24b, xPts per game.

| Area | Attributes | Predicted: lower to 20 | raise to 80 | Gegenpress: lower | raise | Control Possession: lower | raise |
|---|---|---|---|---|---|---|---|
| Chance creation | Anticipation, Off the Ball | −0.099 | +0.014 | −0.079 | +0.021 | −0.082 | +0.011 |
| Pressing intensity | Anticipation, Tackling | −0.088 | +0.012 | −0.081 | +0.019 | −0.066 | +0.005 |
| Out-of-possession shape | Concentration, Marking | −0.050 | +0.007 | −0.024 | +0.001 | −0.029 | +0.017 |
| Passing style | Decisions, Composure | −0.033 | +0.005 | −0.023 | −0.002 | −0.022 | +0.004 |
| Line of engagement | Work Rate, Aggression | −0.024 | +0.014 | +0.002 | +0.005 | +0.009 | +0.004 |
| Pressing trap | Decisions, Positioning | −0.020 | +0.003 | −0.004 | +0.005 | +0.006 | −0.003 |
| Build-up | Technique, Vision | −0.018 | +0.003 | −0.019 | +0.005 | −0.012 | −0.012 |
| In-possession shape | First Touch, team cohesion | −0.012 | +0.002 | −0.015 | −0.010 | −0.008 | −0.017 |

Measured margins: about ±0.022 at 95% for each cell.

- **The losses fit:** predicted and measured correlate 0.94 (Gegenpress) and 0.96 (Control Possession), at 0.77 and
  0.71 of the predicted size; an upper bound should come out above the truth.
- **The asymmetry fits:** because the boost is limited and the baseline already gets most of it, the prediction has
  raising worth about a seventh of lowering for the two leading areas; measured a quarter (Gegenpress) and a ninth
  (Control Possession).
- **Anticipation is the reason for the order.** It's the only one of these attributes with a solid value of its own
  (Study 13b: +0.08 xPts a season per level for one player, against at most +0.05 for Concentration and +0.02 or less
  for the others), and two areas strengthen it. Out-of-possession shape follows through Concentration.
- **Two areas fit less well:** out-of-possession shape costs half its prediction, and line of engagement nothing.
  Their attributes' values are small and partly come from other uses of the attribute.
- **Study 24's first prediction ignored the limit** and gave the right order at twice the size.

## What this means

- **Keep chance creation and pressing intensity up, whatever the style.** Letting either slip from a decent level to a
  low one costs about 3 points a season each; out-of-possession shape about 1.
- **Don't spend training pushing any area above a decent level:** no area pays above it.
- **The other five areas matter little** at this resolution: an area is worth as much as the attributes it
  strengthens, and Positioning, Technique, Vision, Composure, Decisions, Marking, Tackling, Work Rate and Aggression
  are worth little in these matches.

## Caveats

- **Two styles, one squad** (the synthetic Premier League middle eight), familiarity held for every player.
- **The levels are bytes in the record, not the game's displayed familiarity.** 50 is already a high area value
  (about 76); a baseline below that was not tested.
- **The opponents' areas stay at 50** throughout.
- **Study 24's one-at-a-time results** (above) are kept for the record; where they differ (Control Possession), Study
  24b is the more precise.

## Reproduce

```sh
.venv/bin/python port/validation/neutral_study.py build 24 runs/study24
.venv/bin/python port/validation/neutral_study.py pilot runs/study24 --workers 7
.venv/bin/python port/validation/neutral_study.py run runs/study24 --workers 7      # about 2.5 hours with 7 workers
.venv/bin/python port/validation/study24_areas.py runs/study24   # OUT/areas.md
# Study 24b: every area at a random level, from Study 24's scenarios
.venv/bin/python port/validation/study24b_random_areas.py build runs/study24b --from runs/study24
.venv/bin/python port/validation/study24b_random_areas.py run runs/study24b --pilot
.venv/bin/python port/validation/study24b_random_areas.py run runs/study24b --workers 7    # about 4 hours with 7 workers
.venv/bin/python port/validation/study24b_random_areas.py report runs/study24b
```

The specification is `s24` in `port/validation/roadmap_studies.py`; familiarity conditions hold the tested side's
area bytes through the host's `FM27_MAC_EXEC_FIELDS`. The area values were read from the players' records with the
host's record summary (`FM27_MAC_RECORD_SUMMARY=1`) and `port/map/exec_record.py`.
