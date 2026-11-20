# Study 27: what personality is worth

**Question.** How much do four personality values matter for results: Pressure, Professionalism, Sportsmanship and
Temperament?

**Design.** One squad, 10 of its saved matches, each replayed on 30 seeds (300 paired replays per condition). Each
condition sets one value to 1 or to 20 for the whole squad; every condition replays the same matches on the same
seeds as the unchanged squad. 2,700 replays on FM27 27.0.1.

## Results

| Condition | Points per game | xG difference | What changes |
|---|---|---|---|
| Pressure 1 | −0.68 (t −6.8) | −0.38 (t −4.6) | finishing collapses: about 1.9 fewer shots on target a match, goals 0.43 below xG |
| Professionalism 1 | −0.41 (t −4.2) | −0.29 (t −3.6) | less possession, fewer passes and shots |
| Sportsmanship 1 | −0.26 (t −2.7) | −0.29 (t −3.4) | more fouls and cards, broken-up play (17 fewer passes) |
| Temperament 1 | −0.14 (t −1.5) | −0.11 (t −1.3) | +0.4 cards a match |
| Any value at 20 | within ±0.1 | within ±0.15 | nothing clear |

The unchanged squad gets 1.97 points per game. **Low Pressure is the costliest personality trait measured so far:
about −26 points over a 38-game season**, and its effect is mostly in finishing, not in the chances created.
Professionalism and Sportsmanship at 1 also cost clearly. Raising values to 20 adds little for this squad, whose values
are mostly already mid to high.

## How sure

Pressure 1 and Professionalism 1 are solid (|t| > 4); Sportsmanship 1 is clear (t −2.7 for points, −3.4 for xGD);
Temperament 1 is a likely small cost (t −1.5) with a clear effect on cards (t 3.6). One squad and one tactic.

## Mechanism (high level)

Low Pressure acts in three ways, read from the engine (without the formulas):
- **Nerves.** Before and during a match each player has a level of nerves. It rises in big matches, against rivals and
  in close knockout ties, and less so for players with high morale, Pressure, Determination and Important Matches.
  Nerves lower every attribute on the day and make the player's composure and decisions less reliable.
- **Choking.** Every pass, cross and shot can be struck worse when a player's Pressure fails him, more so in big
  matches and most of all for penalties and set pieces. At Pressure 1 this happens on almost every kick, which is why
  finishing collapses.
- **Morale after setbacks.** Players with low Pressure can lose morale after a bad event in the match; the lower the
  Pressure, the more often.

Low Professionalism lowers attributes through the same pre-match state. Low Sportsmanship opens the way to cynical
fouls, and with Temperament it works through bookings and reactions to the referee, which break up the team's play.
Both Pressure and Sportsmanship only bite near the bottom of the scale.

## Which levels and which players

- **Only 1, 10 and 20 have been tested** (Study 11 adds 10 for Pressure and Professionalism, on neutral squads). At 10
  neither costs anything measurable, so the damage starts somewhere below 10; where exactly is unknown.
- **Pressure is worth most in attacking players.** In Study 13b's random configurations (each player's values moved
  ±5 around his own), one level of Pressure in one player was worth about +0.14 goal difference a season for an
  attacking midfielder, less for a striker, and nothing clear for defenders and goalkeepers. That fits choking, which
  costs most where a kick decides a goal. Very low Pressure still hurts every position through nerves.

This agrees with [Study 11](11-hidden-attributes.md), which found Pressure (low) the one clear personality effect and
Temperament driving cards, with fewer pairs. Study 11 measured expected points (from xG), about −0.15 a game for Pressure 1;
the larger loss in real points here is the finishing: xG falls only a little, goals fall much more.

## Reproduce

```sh
.venv/bin/python scripts/study.py new runs/personality --team "Your Club" --newest 10 --seeds 30
.venv/bin/python scripts/study.py add runs/personality profile:pressure=1 profile:pressure=20 \
    profile:professionalism=1 profile:professionalism=20 profile:sportsmanship=1 profile:sportsmanship=20 \
    profile:temperament=1 profile:temperament=20
.venv/bin/python scripts/study.py run runs/personality
.venv/bin/python scripts/study.py report runs/personality
```
