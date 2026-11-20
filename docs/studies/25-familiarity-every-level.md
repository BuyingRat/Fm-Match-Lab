# Study 25: what each tactical familiarity area is worth, at every level

**Status:** done (15-16 November, 80,000 matches). Study 24 compared three levels (20, 50 and 80 in the record). This
study measures the whole curve: each of the eight areas at eight levels from 8 to 95, the value the game shows as the
area's pie on the Tactical Effectiveness panel (full pie = 100). It also tests the three other parts of the
effectiveness record (overall, buy-in and next-match information) and the opponent's familiarity.

**In short:**
- **Chance creation and pressing intensity matter most,** each worth about 6-7 points a season from the bottom of the
  range to the top. Most of it comes from crossing the middle: an area at 58 instead of 37 is worth about 4.5 points
  a season. Beyond that, each step up adds about a point more by 95.
- **Out-of-possession shape is third,** about 3 points a season. It mostly matters to stay above about 40; above 85
  it adds nothing.
- **Build-up gains about 1 point a season above 70.** Passing style, in-possession shape and pressing trap stay within
  about 1 point over their whole range. Line of engagement shows nothing clear.
- **Overall, buy-in and next-match information do nothing measurable** in the match.
- **The opponent's familiarity matters as much as yours:** an opponent with every area at 37 instead of 58 gives you
  about 11 points a season more.
- **The areas add up:** no pair of areas is worth more or less together than apart.

## Design

- **Neutral ground,** as in Study 24: the synthetic Premier League middle-eight squad on both sides, four preset
  opponents (Gegenpress, Control Possession, Park the Bus, Route One), home and away, two template matches between
  other clubs: 16 settings per style.
- **Random levels:** in each configuration every one of eleven parts of the tested side (the eight areas, overall,
  buy-in, next-match information) gets one of eight values at random, independently: 8, 25, 37, 45, 58, 73, 85 or 95.
  The value is the same for every player. The engine reads each area in steps rather than smoothly, and the eight
  values cover all of its steps. The opponent's eight areas are 37, 58 or 85, together.
- **Exact values:** the players' tactical ability and the tactic's complexity were fixed so that each area's value
  came out exactly as set; the values were checked in the players' records.
- **Size:** Gegenpress 3,125 configurations and Control Possession 1,875, each on all 16 settings: 80,000 matches.
- **Analysis:** one regression per style, with seven indicators per part (each value against 45) and a constant per
  setting, gives every part's full curve from every match. The two styles are then pooled.

## Results

Expected points per season (38 games) against an area at 45, both styles pooled. Each value is measured to about
±0.6 points at 95%. **Bold**: established (|t| ≥ 4).

| Area value | 8 | 25 | 37 | 45 | 58 | 73 | 85 | 95 |
|---|---|---|---|---|---|---|---|---|
| Chance creation | **−3.6** | **−3.2** | **−2.5** | 0 | **+2.1** | **+2.4** | **+2.9** | **+3.2** |
| Pressing intensity | **−3.3** | **−3.0** | **−2.7** | 0 | **+1.8** | **+2.8** | **+3.1** | **+3.5** |
| Out-of-possession shape | **−2.3** | **−1.7** | **−1.2** | 0 | +0.2 | +0.8 | **+1.3** | +0.9 |
| Build-up | −0.5 | +0.1 | −0.3 | 0 | +0.6 | **+1.2** | +1.0 | +1.2 |
| Passing style | −0.8 | −0.5 | −0.3 | 0 | +0.3 | +0.4 | +0.5 | +0.7 |
| In-possession shape | −0.6 | −0.2 | −0.2 | 0 | +0.3 | +0.3 | +0.7 | +0.5 |
| Pressing trap | −0.3 | −0.1 | −0.3 | 0 | +0.2 | +0.3 | +0.3 | +0.1 |
| Line of engagement | −1.1 | +0.2 | −0.2 | 0 | −0.4 | −0.6 | −0.8 | −0.5 |
| Overall | +0.1 | −0.2 | 0.0 | 0 | 0.0 | −0.2 | +0.1 | 0.0 |
| Buy-in | +0.1 | +0.3 | +0.5 | 0 | +0.4 | +0.6 | +0.3 | +0.6 |
| Next-match information | +0.5 | 0.0 | −0.2 | 0 | +0.3 | −0.3 | +0.1 | +0.8 |

By style (Gegenpress / Control Possession, per season; margins about ±0.75):

| Area value | 8 | 25 | 37 | 58 | 73 | 85 | 95 |
|---|---|---|---|---|---|---|---|
| Chance creation | −3.8 / −3.2 | −3.8 / −2.2 | −2.8 / −2.0 | +1.7 / +2.6 | +2.2 / +2.8 | +2.9 / +3.0 | +3.0 / +3.5 |
| Pressing intensity | −3.6 / −2.8 | −3.0 / −2.9 | −2.5 / −3.2 | +2.2 / +1.2 | +2.8 / +2.8 | +3.1 / +2.9 | +3.9 / +2.9 |
| Out-of-possession shape | −1.9 / −3.0 | −1.3 / −2.4 | −1.0 / −1.7 | +0.5 / −0.3 | +1.0 / +0.5 | +1.6 / +0.9 | +1.5 / 0.0 |
| Build-up | −0.7 / 0.0 | +0.1 / +0.2 | −0.3 / −0.2 | +0.8 / +0.2 | +1.2 / +1.1 | +1.2 / +0.8 | +1.4 / +0.8 |
| Passing style | −0.6 / −1.1 | −0.5 / −0.5 | −0.4 / −0.1 | +0.2 / +0.3 | +0.2 / +0.8 | +0.7 / +0.1 | +0.6 / +0.8 |
| In-possession shape | −0.8 / −0.3 | −0.5 / +0.4 | −0.4 / +0.2 | +0.2 / +0.5 | +0.1 / +0.7 | +0.6 / +0.8 | +0.6 / +0.2 |
| Pressing trap | −0.5 / 0.0 | −0.5 / +0.5 | −0.5 / +0.2 | −0.1 / +0.6 | +0.1 / +0.5 | +0.2 / +0.4 | −0.1 / +0.4 |
| Line of engagement | −0.7 / −1.8 | +0.4 / −0.2 | 0.0 / −0.6 | −0.5 / −0.3 | −0.3 / −1.1 | −0.8 / −0.8 | −0.6 / −0.4 |

- **The styles agree for six of the eight areas.** Two differ slightly (p 0.01-0.05, which one or two of eight tests
  can reach by chance): out-of-possession shape keeps gaining above 58 only in Gegenpress, and Gegenpress loses a little
  more at low chance creation.
- **Both ends of the pitch:** chance creation and pressing intensity move xG for and xG against by similar amounts,
  so a well-trained side creates more and concedes less.
- **The opponent's areas** (all eight together, per game against 58): at 37 the tested side gains +0.29 expected points
  (t 38 to 48), at 85 it loses −0.10 (t −13 to −15). That's +11 and −3.7 points a season.
- **The areas add up.** All 28 pairs of areas were tested for an interaction: chi-square 27 on 28 degrees of freedom
  (Control Possession) and 33 on 28 (Gegenpress), as expected by chance.

## Mechanism (high level)

Each area strengthens particular attributes of every player during play. Chance creation and pressing intensity both
strengthen Anticipation, the mental attribute with the clearest value of its own (Study 13b), which is why they lead
in both styles; out-of-possession shape strengthens Concentration. The engine reads each area in steps, and the
strengthening it gives is limited, so the curve is steep in the middle and flat at the top: the largest step is from
below 45 to above 51.

## What this means

- **Keep chance creation and pressing intensity high,** whatever the style: about 3 points a season each separate
  "trained" (85+) from "middling" (45), and as much again from "poor" (25).
- **Keep out-of-possession shape above about 40;** pushing it past 85 adds nothing.
- **The other five areas are worth about a point a season or less each.** Training time is better spent on the top
  three.
- **The realistic range in the game is about 35-100:** even with no training and no matches, a player's tactical
  ability and the tactic keep areas at about 35-40. The values below 35 show the engine's response, not a situation
  you're likely to see.

Study 29 tests what this means for a whole training split, head to head.

## Caveats

- **One squad (the synthetic middle eight), two styles,** and every player at the same value. Whether a striker's
  chance creation is worth more than a defender's isn't measured here.
- **Values relative to 45.** Compare levels within an area, or areas at the same level.
- **The opponent's eight areas moved together,** so the study can't say which of the opponent's areas matter, or
  whether a weak area costs more against an opponent strong in the matching one.

## Reproduce

```sh
.venv/bin/python port/validation/study25_familiarity.py build runs/study25a --from runs/study24
.venv/bin/python port/validation/study25_familiarity.py run runs/study25a --pilot
.venv/bin/python port/validation/study25_familiarity.py run runs/study25a --workers 7    # about 15 hours
.venv/bin/python port/validation/study25_familiarity.py report runs/study25a           # report.md, effects.json
```

It needs Study 24's settings (`runs/study24`, built by `neutral_study.py build 24`).
