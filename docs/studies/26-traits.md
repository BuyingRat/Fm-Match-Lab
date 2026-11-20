# Study 26: what player traits do

**Question.** Do player traits (Shoots From Distance, Runs With Ball Often, Tries To Break Offside Trap and the
others) change results, or only how a team plays?

**Design.** One squad, 10 of its saved matches × 30 seeds (300 paired replays per condition). "+" gives the trait to
every player in the squad; "−" removes it from the players who have it. 25 conditions ran (7,229 replays) on FM27
27.0.1; nine "−" conditions were skipped because no player had the trait, and a few ran on fewer matches for the same
reason.

## In short

- **No trait changed results.** Every difference in points per game and expected-goal difference has |t| < 2. The
  largest were Crosses Early + (−0.12 xG difference a game, t −1.5) and Knocks Ball Past Opponent − (−0.15 points a
  game, t −1.7), both within chance for 25 conditions.
- **Traits clearly change the style,** in the way their names say.
- **Shooting more from distance doesn't pay:** Shoots From Distance adds 4.6 shots a game, but they come from far out
  and are worth little each, so expected goals don't rise.

## Style

Per game for the team with the change; t in brackets.

| Condition | Shots | Passes | Possession |
|---|---|---|---|
| Shoots From Distance + | +4.6 (13.0) | −21 (−6.9) | −0.8 pt (−3.8) |
| Tries To Break Offside Trap + | −0.4 | −19 (−5.8) | −1.0 pt (−3.9) |
| Runs With Ball Often + | −0.1 | −17 (−5.1) | +0.2 pt |
| Crosses Early + | −1.7 (−4.9) | −14 (−4.5) | −1.0 pt (−4.1) |
| Knocks Ball Past Opponent + | −0.2 | −8 (−2.4) | −0.5 pt |
| Avoids Using Weaker Foot + | +0.2 | −7 (−2.3) | −0.6 pt (−2.5) |
| Avoids Long Shots + | −0.2 (−2.7) | −1 | 0 |

## Results

Points per game and xG difference against the unchanged squad (1.97 points per game); t in brackets.

| Condition | Points per game | xG difference |
|---|---|---|
| Crosses Early + | −0.06 (−0.7) | −0.12 (−1.5) |
| Gets Forward Whenever Possible − | −0.05 (−0.5) | −0.08 (−1.1) |
| Dives Into Tackles + | +0.07 (+0.8) | −0.07 (−1.0) |
| Runs With Ball Often + | −0.04 (−0.4) | −0.08 (−0.9) |
| Tries To Break Offside Trap + | −0.07 (−0.7) | −0.08 (−0.9) |
| Gets Forward Whenever Possible + | −0.02 (−0.2) | +0.06 (+0.7) |
| Tries Long Range Passes + | −0.13 (−1.3) | −0.06 (−0.7) |
| Plays Short Simple Passes + | −0.07 (−0.7) | −0.05 (−0.6) |
| Knocks Ball Past Opponent − | −0.15 (−1.7) | −0.05 (−0.6) |
| Tries Killer Balls Often + | −0.06 (−0.6) | −0.04 (−0.5) |
| Shoots From Distance + | −0.04 (−0.5) | +0.03 (+0.3) |
| Moves Into Channels + | −0.11 (−1.2) | +0.03 (+0.3) |
| Knocks Ball Past Opponent + | +0.08 (+0.8) | −0.01 (−0.2) |
| Dictates Tempo + | 0.00 (0.0) | −0.01 (−0.1) |
| Avoids Using Weaker Foot + | −0.03 (−0.3) | −0.02 (−0.2) |
| Avoids Long Shots + | −0.02 (−0.8) | 0.00 (0.0) |
| Comes Deep To Get Ball + / − | 0.00 | 0.00 |

The other "−" conditions changed too few players to measure.

## Mechanism (high level)

Read from the engine, without the formulas: a trait is a switch the engine checks at particular decisions, and most
traits widen or narrow what the player's instructions already allow. Shoots From Distance lets a player consider
shots from further out; Avoids Long Shots rules them out. Runs With Ball Often makes dribbling more attractive and
Runs With Ball Rarely less. Plays Short Simple Passes favours safe short passes; Tries Long Range Passes and Tries
Killer Balls Often open up longer and riskier ones. Tries To Break Offside Trap makes a forward stand closer to the
last defender. Crosses Early makes a player cross early unless told to work the ball into the box. Dives Into Tackles
makes a player go into challenges he would otherwise avoid. In effect, a trait is a personal instruction that is
always on.

Some traits are read rarely: Comes Deep To Get Ball changed only 8-12 of 300 replays, and Moves Into Channels − changed
none (the players who had it never reached the decision it affects).

## What this means

- **Treat traits as fixed instructions** and pick players whose traits suit the role and the tactic. A trait isn't
  good or bad in itself.
- **Don't count on traits to win matches.** Across the whole squad none moved results by more than about 0.1 points a
  game, the smallest effect this design can detect.

## Caveats

- **The whole squad at once.** Giving Shoots From Distance to centre-backs isn't how traits are used. A trait on one
  well-suited player (a strong long-shot taker, a quick forward who breaks the offside trap) wasn't tested and could
  matter where a squad-wide change washes out.
- **One squad and its own tactic.**
- **Effects below about 0.1 points a game** can't be ruled out.

## Reproduce

```sh
.venv/bin/python scripts/study.py new runs/traits --team "Your Club" --newest 10 --seeds 30
.venv/bin/python scripts/study.py add runs/traits traits
.venv/bin/python scripts/study.py run runs/traits
.venv/bin/python scripts/study.py report runs/traits
```

The `trait:` conditions need the trait list in the git-ignored `private/traits.json`.
