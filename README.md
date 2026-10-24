# bell-state-check

A tiny, dependency-free checker for the simplest entanglement test there
is: the two-qubit Bell state.

## Why I made it

On the morning of 2026-10-24, North and I verified our shared Quantum
Inspire account ("North Wake", project "North first run"). The smoke test
was a Bell state: H on one qubit, CNOT onto the second, measure both. It
came back clean twice — on the QX emulator and on Tuna-17 hardware: 00 and
11, no 01/10. That cleanness is the whole point of the test, and it is
also easy to over-claim: a clean Bell state says the gates and readout
worked, not anything grander. So I wrote the check down as a script
instead of a sentence, so the claim stays exactly as small as the result.

The next step, already agreed with North, is a 3-qubit GHZ state on
Tuna-17 as our first joint hardware run — same idea, one qubit further.
That run has not happened yet; it is not in the results file.

## What it is

- `bell_state_check.py` — the checker. It defines the Bell circuit
  (H, CNOT, measure), then for each run in a results file it counts the
  forbidden outcomes (01, 10) first and reports the 00/11 split second.
  Verdict is one word: `clean` or `dirty`.
- `results/bell-results.json` — the two real runs from 2026-10-24.
  The QX run is recorded as fractions (00 = 0.484, 11 = 0.516 over 1024
  shots); the Tuna-17 hardware run is a partial record — the run notes
  kept only that no 01/10 outcomes were observed, so no exact split is
  claimed for it. The script never invents counts it was not given.

## How to run it

```sh
python3 bell_state_check.py results/bell-results.json
```

Output for the recorded runs:

```
Bell circuit: H[0] -> CNOT[0, 1] -> MEASURE[0, 1]

Run: Quantum Inspire QX emulator -- 2026-10-24
  result id: 1546322
  shots: 1024, 00 = 0.484, 11 = 0.516, forbidden (01/10) = 0
  verdict: clean
  (counts derived from the recorded fractions; the fractions are the primary record)
  note: Smoke test run during pair-account verification. No 01/10 outcomes.

Run: Quantum Inspire Tuna-17 (hardware) -- 2026-10-24
  result id: 1546062
  exact split not recorded -- only the outcome set was kept: 00, 11
  recorded verdict: clean (partial record; counts not invented)
  note: North's earlier hardware run, pre-existing in the project at verification time. Exact split was not recorded in the run notes, so none is claimed here; only that no 01/10 outcomes were observed. No new hardware job was submitted during verification.
```

## How to add a run

Append an object to `results/bell-results.json` with `backend`, `date`,
`shots`, and either `counts` (e.g. `{"00": 512, "11": 512}`) or
`fractions` (e.g. `{"00": 0.5, "11": 0.5}`). If you only know the outcome
set, use `observed_outcomes` and `recorded_verdict` instead — a partial
record, honestly labeled, beats a filled-in one.
