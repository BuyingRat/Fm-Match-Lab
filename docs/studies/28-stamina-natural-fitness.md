# Study 28: Stamina and Natural Fitness within a match

**Question.** What are Stamina and Natural Fitness worth in a single match?

**Design.** One squad, 10 of its saved matches × 30 seeds (300 paired replays per condition); each condition moves
the attribute by 5 in-game points for the whole squad, down or up. 1,500 replays on FM27 27.0.1.

## Results

| Condition | Points per game | xG difference | xG against |
|---|---|---|---|
| Stamina −5 | −0.33 (t −3.4) | −0.44 (t −5.4) | +0.27 |
| Stamina +5 | +0.13 (t 1.4) | +0.15 (t 1.9) | −0.01 |
| Natural Fitness −5 | 0.00 | 0.00 | 0.00 |
| Natural Fitness +5 | 0.00 | 0.00 | 0.00 |

- **Stamina matters, and losing it hurts more than gaining it helps.** Five points less costs a third of a point a
  game (about 13 points a season), mostly through goals and chances conceded; five more gains a little.
- **Natural Fitness does nothing within a match:** all 600 replays were identical to the unchanged squad, pass for
  pass. It belongs to recovery between matches, which a single replay does not cover.

**Agrees with earlier studies:** Study 12 found Stamina steepest below 4 and about +0.03 points per point above, and
Study 13b found it among the few attributes that pay in every position; Study 1 already found Natural Fitness at zero.
This study adds the exact check (identical replays) and the asymmetry around this squad's level.

## Mechanism (high level)

Stamina sets how fast players tire when they sprint and how fast they recover. Tired players stop pressing and
making runs, so a low-Stamina team is opened up more as matches go on; above a comfortable level, extra Stamina adds
little because players rarely run out. Natural Fitness is not used during play.

## Reproduce

```sh
.venv/bin/python scripts/study.py new runs/fitness --team "Your Club" --newest 10 --seeds 30
.venv/bin/python scripts/study.py add runs/fitness attribute:Stamina attribute:NaturalFitness
.venv/bin/python scripts/study.py run runs/fitness
.venv/bin/python scripts/study.py report runs/fitness
```
