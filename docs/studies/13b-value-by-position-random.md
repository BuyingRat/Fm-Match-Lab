# Study 13b: what is an attribute worth in each position? Random configurations

**Status:** done (14 November): Gegenpress 50,000 matches; Catenaccio 34,340 (stopped early to free the machine;
resumable). Study 13 changed one attribute in one
position group at a time and found no clear position-specific values. A test posted on FM Arena (Purity, 200,000
matches on their own 3-4-2-1) used a different design and did find them. Is the difference the design, the tactic,
or chance? And can the same design finally measure single goalkeeper attributes, which Study 21 could not?

**In short:**
- **Positions do differ.** With every attribute of every starter changed at random in every match, 50,000 matches
  measure all 48 outfield attributes in five positions, and the goalkeeper's, to about ±0.03 expected points a season
  per level. Ten attributes differ between positions beyond chance (2.4 expected); Jumping Reach, Pace, Balance and
  Acceleration clearly (p < 0.005).
- **The same few attributes lead everywhere:** Acceleration, Pace, Jumping Reach, Stamina, Anticipation. What changes
  with the position is how much, and whether it works in attack or defence.
- **Jumping Reach is a centre-back's and a striker's attribute** (+0.32 and +0.19 xPts a season per level), much less a
  defensive midfielder's (+0.06). Balance also pays for centre-backs and strikers, hardly elsewhere.
- **Goalkeepers: Agility and Reflexes matter, each on its own.** +1 level of either saves about 0.8-1.1 goals a season
  (t −19 to −23), worth about half a point; +5 of each is worth up to 5 points a season together (gains look
  smaller than losses: a lead). The xG the keeper
  faces doesn't change: it is all at the save, so xPts tables miss it.
- **The style changes the sizes, not the order.** Catenaccio, a deep 5-2-2-1 close to Purity's shape, gives the same
  leaders and the same goalkeeper result, but its defenders gain less from speed (less space to cover behind them)
  and its central attacking midfielders more (correlation with Gegenpress 0.85; the differences are beyond chance).
- **This agrees with Study 13 and, in pattern, with Purity's table.** Study 13's numbers fit these within its noise;
  it lacked the precision to separate positions. Purity's goal-difference weights correlate 0.80 with ours over 240
  cells, but their striker values are two to three times ours, in both styles. A lone striker is not the reason:
  Catenaccio's lone striker gains no more than each of Gegenpress's two. The difference is unexplained (their real
  players, roles, fixtures or method).

## Design

- **Random configurations,** as in Purity's test: in each match, every attribute of every starter of the tested side
  moves by +5 or −5 at random (clamped to 1-20), independently. One regression on the per-position sums of the changes
  then estimates every attribute in every position at once, from the same matches.
  - **Fields:** 52 attributes (all except the feet) and the seven personality attributes. The eleven goalkeeping
    attributes are changed for the goalkeeper only.
  - **Positions:** goalkeeper; full-backs (DL, DR); centre-backs (DCL, DCR); defensive midfielders (DML, DMR); wide
    attacking midfielders (AML, AMR); strikers (STL, STR). Each estimate is for **one** player of the group.
- **Neutral ground,** as in Study 13: the synthetic Premier League middle-eight squad on both sides, Gegenpress for the
  tested side, tactical familiarity held at 80, four preset opponents home and away, two template matches between
  other clubs: 16 settings, each with its own constant in the regression.
- **50,000 matches,** one configuration each, on its own seed.
- **Checks before the run:** on fabricated results with known effects the analysis recovered them (Pace for the
  striker 0.0085 for a true 0.010, goalkeeper Reflexes on xG against −0.0073 for −0.008); 4.5% false |t| > 2, 1 false
  confirmation in 292, 6.5% false position differences. A 320-match pilot played every configuration with every change
  accepted by the game's validator.
- **Confirmed** (*) means |t| > 2 in both random halves of the configurations, with the same sign.

**Units:** per season (38 games), for +1 level in one player of the position. Multiply by 5 for a +5 change, by the
number of players for a whole group.

## Expected points by position

The attributes with any effect above ±0.04; the other 34 outfield attributes are within ±0.04 in every position and
mostly within ±0.02. Typical 95% margin ±0.03.

| Attribute | Team (per player) | ST | AM | DM | FB | CB | Positions differ? (p) |
|---|---|---|---|---|---|---|---|
| Acceleration | +0.18 | +0.20* | +0.15* | +0.15* | +0.17* | +0.20* | 0.003 |
| Pace | +0.16 | +0.21* | +0.17* | +0.12* | +0.17* | +0.13* | < 0.001 |
| Jumping Reach | +0.13 | +0.19* | +0.10* | +0.06 | +0.08* | **+0.32*** | < 0.001 |
| Stamina | +0.09 | +0.07* | +0.10* | +0.09* | +0.10* | +0.08* | 0.50 |
| Anticipation | +0.08 | +0.10* | +0.07* | +0.07* | +0.07* | +0.10* | 0.20 |
| Balance | +0.06 | +0.09* | +0.03 | +0.04 | +0.06* | +0.10* | < 0.001 |
| Dribbling | +0.05 | +0.05* | +0.07* | +0.02 | +0.08* | +0.03 | 0.004 |
| Concentration | +0.05 | +0.06* | +0.03 | +0.02 | +0.07* | +0.05* | 0.08 |
| Vision | +0.02 | +0.02 | +0.01 | +0.05* | −0.00 | +0.03 | 0.08 |
| Strength | +0.03 | +0.03 | +0.02 | +0.04 | +0.02 | +0.04 | 0.81 |

- **Ten of 48 attributes differ between positions at p < 0.05** (2.4 expected by chance); Jumping Reach, Pace, Balance
  (p < 0.001) and Acceleration (0.003) clearly.
- **Strikers gain most** from Pace and Acceleration, then Jumping Reach and Balance; **centre-backs** from Jumping Reach, Acceleration,
  Balance and Anticipation; **full-backs** from Pace, Acceleration, Dribbling and Concentration; **defensive
  midfielders** least from almost everything (Vision is the only attribute where they lead).
- **Technical and mental attributes show almost nothing** in any position: Passing, Technique, Tackling, Marking,
  Positioning, Crossing, Decisions, Composure, First Touch, Off the Ball, Flair are within ±0.04 everywhere.

## How each position's attributes work

xG for and against per season, +1 level for one player (t in brackets):

| | Striker | Wide attacker | Defensive midfielder | Full-back | Centre-back |
|---|---|---|---|---|---|
| Pace | xG for +0.35 (+22) | +0.18 for, −0.10 against | −0.16 against (−10) | −0.21 against (−14) | −0.18 against (−12) |
| Acceleration | xG for +0.28 (+17) | +0.17 for, −0.10 against | −0.16 against (−10) | +0.13 for, −0.17 against | −0.30 against (−20) |
| Jumping Reach | xG for +0.23 (+14) | +0.12 for (+7) | −0.08 against (−5) | −0.13 against (−8) | **+0.25 for, −0.30 against** |
| Stamina | xG for +0.13 (+8) | +0.10 for, −0.07 against | −0.14 against (−9) | −0.12 against (−8) | −0.10 against (−6) |
| Balance | xG for +0.14 (+9) | nothing | nothing | −0.07 against (−4) | −0.14 against (−9) |

- **The same attribute does different jobs.** For a striker, speed and jumping create chances; for a defender they
  prevent them. A centre-back's Jumping Reach does both (set pieces at both ends).
- **Finishing and Strength work through conversion,** not chances, so expected points don't show them. Goals for, per
  level:
  - Finishing: striker +0.21 (t 7.5), wide attacker +0.09 (t 3.2), at the same xG.
  - Strength: striker +0.18, wide attacker +0.19 (t 6-7), against +0.06 xG.

## Goal difference

Goals for minus against per season, per level for one player; typical 95% margin ±0.08. Points follow the same
pattern (about 0.6 points per goal) with twice the noise of expected points.

| Attribute | ST | AM | DM | FB | CB |
|---|---|---|---|---|---|
| Acceleration | +0.49* | +0.24* | +0.27* | +0.29* | +0.41* |
| Pace | +0.45* | +0.27* | +0.26* | +0.36* | +0.31* |
| Jumping Reach | +0.34* | +0.21* | +0.09 | +0.11 | +0.44* |
| Stamina | +0.15* | +0.16* | +0.20* | +0.25* | +0.20* |
| Balance | +0.21* | +0.00 | +0.06 | +0.09 | +0.24* |
| Strength | +0.16* | +0.14* | +0.15* | +0.09 | +0.17* |
| Finishing | +0.21* | +0.06 | +0.04 | +0.00 | +0.04 |
| Anticipation | +0.13 | +0.11 | +0.10 | +0.14 | +0.15 |
| Concentration | +0.08 | +0.06 | +0.08 | +0.19* | +0.12 |

## The goalkeeper

Per season, +1 level of the goalkeeper's attribute; t in brackets. The rest are within ±0.1 goals and |t| < 2.

| Attribute | Goals against | xG against | Points | Expected points |
|---|---|---|---|---|
| Agility | **−0.93 (−23)** | −0.01 (−0.3) | **+0.58 (+13.5)** | −0.02 |
| Reflexes | **−0.76 (−19)** | +0.01 (+0.4) | **+0.50 (+11.6)** | −0.01 |
| Aerial Reach | −0.23 (−4.0) | −0.06 (−1.9) | +0.16 (+2.5) | +0.03 |
| Acceleration | −0.15 (−3.8) | −0.21 (−9.8) | +0.16 (+3.7) | +0.15 |
| Determination | −0.13 (−3.2) | −0.04 (−1.7) | +0.12 (+2.8) | +0.03 |
| Handling | −0.11 (−2.7) | −0.09 (−4.2) | +0.05 (+1.2) | +0.06 |
| Concentration | −0.08 (−1.9) | −0.01 | +0.07 | +0.02 |
| Positioning | −0.02 | −0.04 | +0.05 | +0.02 |
| One on Ones | −0.00 | +0.02 | +0.06 | +0.02 |

- **Agility and Reflexes are shot-stopping:** goals against fall, xG against doesn't move. +5 in both saves about 8.5
  goals and is worth about 5 points a season.
- **Acceleration and Handling act on the chances themselves:** they lower the xG the keeper faces (a keeper who comes
  off his line sooner; fewer rebounds), worth less in goals.
- **The gain from a better keeper is smaller than the loss from a worse one:** the earlier studies' +5 conditions
  saved about 0.6 of what these coefficients predict (pooled estimates, below). Read the +5 figures as the upper end.
- **Study 21's leads don't hold:** Positioning and Concentration are close to zero here.
- **Consistent with Study 21.** There, Reflexes and Agility +5 alone lowered goals against by 0.06 and 0.05 per game
  (t below 1), and 0.14 together. Here +5 is 0.10 and 0.12 per game each: within Study 21's error, which was about
  ±0.15. Study 21 was right that the effects are real but too small for 400 pairs; 50,000 random configurations
  resolve them.

## Against Study 13 and Purity's test

- **Study 13** (+5 for the two players of a group, 320 pairs each): its 40 cells match this study's predictions within
  noise (chi-square 36 on 40). Its "no position differences" was a lack of power: its margin, ±0.08 xPts per game,
  is about the size of the largest differences here (Jumping Reach for two centre-backs +0.08 per game, for two
  defensive midfielders +0.02).
- **Study 13's "the first players are worth more" (Jumping Reach)** is much weaker here. With ten players each at +5
  or −5, a pairwise interaction would show as diminishing returns: −0.03 xPts a season per pair of +5 players (t −2.1),
  about a fifth of the main effect when all ten are +5. Study 13's first three players included a centre-back and a
  striker, the two positions where Jumping Reach is worth most: this study predicts those three give 44% of the team's
  gain, against Study 13's 64% (t about 2 there). Position, not diminishing returns, explains most of that finding.
- **Purity's test** (Brentford's 3-4-2-1, real players and fixtures, goals per season):
  - The pattern agrees: correlation 0.80 over 240 attribute × position cells; the same top five; the same positions
    for Jumping Reach (striker and centre-back, little for defensive midfielders); Finishing only for forwards;
    technical attributes near zero.
  - **The size differs for the striker:** ours are about half theirs (Pace +0.45 against +0.90, Jumping Reach +0.34
    against +0.73). It isn't the number of strikers: Catenaccio's lone striker gets Pace +0.27 and Jumping Reach +0.21,
    no more than each of Gegenpress's two, and Catenaccio is the closer match to their shape (correlation 0.67, its
    striker a third of theirs). Their striker is a real player in their own role, against real
    opponents; ours are synthetic. Other positions are within about 30% for Gegenpress.
  - **The goalkeeper** was not covered in their test.

## Catenaccio: does the style change the weights?

Catenaccio plays a 5-2-2-1: three centre-backs, two wing-backs (here in the full-back group), two defensive
midfielders, two central attacking midfielders (here in the attacking-midfield group, central rather than wide) and
one striker. 34,340 matches, so margins are about 20% wider than for Gegenpress (±0.04 xPts per season per level).

Expected points per season, +1 level for one player:

| Attribute | Style | ST | AM | DM | FB | CB |
|---|---|---|---|---|---|---|
| Acceleration | Gegenpress | +0.20 | +0.15 | +0.15 | +0.17 | +0.20 |
| | Catenaccio | +0.17 | +0.21 | +0.15 | +0.14 | +0.13 |
| Pace | Gegenpress | +0.21 | +0.17 | +0.12 | +0.17 | +0.13 |
| | Catenaccio | +0.20 | +0.24 | +0.04 | +0.13 | +0.06 |
| Jumping Reach | Gegenpress | +0.19 | +0.10 | +0.06 | +0.08 | +0.32 |
| | Catenaccio | +0.16 | +0.13 | +0.07 | +0.09 | +0.23 |
| Stamina | Gegenpress | +0.07 | +0.10 | +0.09 | +0.10 | +0.08 |
| | Catenaccio | +0.07 | +0.09 | +0.05 | +0.08 | +0.03 |
| Anticipation | Gegenpress | +0.10 | +0.07 | +0.07 | +0.07 | +0.10 |
| | Catenaccio | +0.11 | +0.07 | +0.05 | +0.03 | +0.05 |
| Balance | Gegenpress | +0.09 | +0.03 | +0.04 | +0.06 | +0.10 |
| | Catenaccio | +0.06 | +0.07 | +0.07 | +0.02 | +0.04 |
| Dribbling | Gegenpress | +0.05 | +0.07 | +0.02 | +0.08 | +0.03 |
| | Catenaccio | +0.05 | +0.10 | +0.02 | +0.09 | −0.01 |

- **The same leaders:** Acceleration, Jumping Reach and Pace in both, then Stamina, Anticipation, Balance, Dribbling,
  Concentration. Over all 240 outfield cells the two styles correlate 0.85 (expected points) and 0.71 (goal
  difference).
- **But the styles differ beyond chance** (chi-square 388 on 240 in expected points). The largest differences:
  - **Centre-backs gain less in Catenaccio** from Acceleration, Pace, Jumping Reach, Balance and Stamina (each
    t 3-4), probably because defending deep leaves less space behind them and three share the work instead of two.
  - **Defensive midfielders' Pace** is worth +0.04 in Catenaccio against +0.12.
  - **Central attacking midfielders gain more** from Pace (+0.24 against +0.17 for Gegenpress's wide ones).
- **Positions differ in Catenaccio too:** ten attributes at p < 0.05 (2.4 expected); Pace, Jumping Reach,
  Acceleration, Dribbling and Concentration at p < 0.005.
- **Conversion again for forwards:** Finishing adds goals at the same xG (central attacking midfielder +0.12 a season
  per level, t 4.1; striker +0.09, t 2.1), and so does Strength (+0.09 to +0.11).
- **The goalkeeper result repeats:** Agility −1.09 goals against a season per level (t −23), Reflexes −0.93 (t −20),
  with no change in xG against; Acceleration lowers xG against (−0.28, t −11). Handling shows nothing in Catenaccio
  (+0.02).

## Checks against the other studies, and what the same matches say about curvature

**The model predicts the earlier studies.** Every condition of Studies 9b, 10, 11, 12, 13, 14, 14b, 21 and 21b played in
this set-up (247 conditions, about 100,000 matches) was rebuilt to see exactly which players and attributes it
changed, and predicted from this study's per-level coefficients (`port/validation/pooled_attributes.py`):
- **Predicted and measured agree:** correlation 0.94 in expected points. Within the range measured here (changes of
  ±5, levels 9-20) the 187 conditions fit within their noise (chi-square 133 on 179), once each study's baseline is
  allowed its own offset (see below).
- **One position group at a time (Study 13): exactly additive,** measured = 0.96 × predicted (±0.16).
- **The whole squad +5: 1.23 × predicted** (±0.09) with the starters alone. The substitutes explain most of the rest
  (pooled estimates, below).
- **Below level 9 the straight line breaks** (Study 12's levels 1-6): Pace and Acceleration lose about 50% more than
  linear, Work Rate collapses (its floor), and Jumping Reach loses less (it is convex, below).
- **Each study's baseline carries its own luck.** Pairing on seeds barely reduces noise (one change alters the whole
  match), so every condition compared with the same unchanged matches shares their error: Studies 14 and 14b read
  about 0.04-0.05 xPts per game high for every condition, Study 12's baseline converted chances poorly (1.27 goals
  from 1.47 xG), which shows as more goals for every condition. Comparisons between conditions are unaffected.

**Curvature and combinations, from the same 50,000 matches** (`port/validation/random_curvature.py`): starters begin
at different levels, so the value of a level can be compared between players of the same position.
- **Jumping Reach is strongly convex** (t 7.0): each level is worth about 0.028 xPts a season more per level the
  player already has. Roughly nothing for a player at 7, about 0.29 for one at 17. This matches Study 12 (it pays
  above 9-12) and Purity's finding.
- **No other attribute's value depends on the starting level** within 8-17 (Pace, Acceleration, Stamina,
  Anticipation, Balance, Dribbling, Concentration, Strength: |t| < 1.7).
- **Pace and Acceleration reinforce each other in the same player** (t 3.7): +5 in both is worth about 7% more than
  the two separately. Of seven other pairs tested, Jumping Reach × Heading (more, in goals, t 2.7) and Passing × Vision
  (less, t −2.4) are leads only.

**Pooled estimates: everything together** (`pooled_attributes.py minutes` and `pool`, no new study matches):
- **Substitutes, credited by their minutes.** 320 of Study 13's unchanged matches, replayed with every substitution
  recorded, give each bench player's minutes per position: the substitutes play about 104 minutes a match between
  them, mostly as wide or attacking midfielders (the starters there play 71 minutes on average, defensive midfielders
  83, everyone else about 90). A substitute's +1 level is then worth the position's coefficient times its minutes
  there over a starter's.
- **With the substitutes, the whole-squad conditions fit:** measured = 1.02 × predicted (±0.07; 1.14 with the
  starters alone), and their spread is within the noise (chi-square 27 on 47). The excess was the substitutes, not a
  gain from improving everyone at once.
- **One linear model explains every earlier condition in its range** (changes of at most 5 levels): 105 conditions,
  measured = 0.96 × predicted (±0.06) in expected points, chi-square 110 on 105. Each study, left out of the fit and
  predicted from the rest, agrees within its noise; Study 13 is borderline (chi-square 56 on 39, p 0.04).
- **Jumping Reach is the exception:** its 15 conditions measure 1.26 × the prediction (±0.08), as its convexity
  predicts for players above the squad's average level, so they are left out of the fit.
- **Pooling sharpens the estimates only a little:** the earlier studies change whole positions or squads at once, so
  they mostly add to the whole-team values (standard errors 5-17% smaller for 18 attributes, e.g. Anticipation
  +0.82 ± 0.05 a season for every starter +1, Dribbling +0.50 ± 0.05, Pace +1.56 ± 0.06), and almost nothing to
  single positions (at most 5%, except the goalkeeper's One on Ones, close to zero either way). The estimates
  hardly move: this study's numbers stand.
- **Goalkeepers, in goals against: a gain is worth less than a loss.** The conditions that improve the goalkeeper
  (Studies 10, 14, 14b, 21, 21b; +5 from the keeper's own level) lower goals against by only 0.58 × the prediction
  (±0.09; expected points fit, 0.98). This study's design moves each attribute 5 levels down or up, so its
  coefficient is half that swing. Read together: a keeper 5 levels worse in Agility or Reflexes costs about 2.4 times
  what one 5 levels better saves. A lead, to be confirmed by a study that lowers the keeper's attributes.

## What this means

- **Recruit by position for the physical attributes:** Pace and Acceleration everywhere; Jumping Reach and Balance for
  centre-backs and strikers; Stamina for full-backs and midfielders; Finishing and Strength for forwards (goals, not
  xG).
- **Goalkeepers: Agility and Reflexes first,** then Aerial Reach. Don't pay for One on Ones, Positioning or
  Concentration on this evidence.
- **Most technical and mental attributes are worth little anywhere** in these matches, as in Studies 1 and 13.

## Caveats

- **Two styles.** The order holds across them, the sizes don't: read the numbers as typical, not exact for another
  tactic.
- **Catenaccio stopped at 34,340 of 50,000 matches**; it can be resumed with the same `run` command.
- **One synthetic squad,** levels mostly 6-18. Each estimate is the average slope over a ±5 range; a two-level design
  can't show curvature within it (Study 12 measured that).
- **Single matches:** no injuries, fitness or form over a season, so Natural Fitness and Injury Proneness can't show.
- **Personality attributes** are changed as the match sees them; their effects (Pressure, Important Matches,
  Determination) are small and mostly unconfirmed.

## Reproduce

```sh
.venv/bin/python port/validation/random_study.py build runs/random/gegenpress --configs 50000 --style Gegenpress
.venv/bin/python port/validation/random_study.py pilot runs/random/gegenpress --workers 7
.venv/bin/python port/validation/random_study.py run runs/random/gegenpress --workers 7     # about 10 hours with 7 workers
.venv/bin/python port/validation/random_study.py report runs/random/gegenpress
```

Catenaccio: the same with `--style Catenaccio` and `runs/random/catenaccio`.

Against the other studies and pooled (needs their results in `runs/roadmap/`; `presets.jsonl` from `runs/roadmap/13`
in `runs/pooled/scratch/`):

```sh
.venv/bin/python port/validation/pooled_attributes.py designs runs/pooled     # what each earlier condition changed
.venv/bin/python port/validation/pooled_attributes.py predict runs/pooled
.venv/bin/python port/validation/pooled_attributes.py minutes runs/pooled     # 320 matches: substitutes' minutes
.venv/bin/python port/validation/pooled_attributes.py pool runs/pooled        # runs/pooled/pool.md, pool.json
```

Regression: the outcome on the per-position sums of the level changes (one column per attribute and position), with a
constant per setting; the team model has one column per attribute for the ten outfield players. Position differences:
a Wald test that the five outfield coefficients are equal (4 degrees of freedom).
