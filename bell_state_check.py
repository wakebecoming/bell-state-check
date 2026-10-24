#!/usr/bin/env python3
"""Bell-state check: is a two-qubit result actually entangled, or just noise?

The Bell state (|00> + |11>) / sqrt(2) is made with two gates:

    H on qubit 0, then CNOT with qubit 0 as control and qubit 1 as target.

Measured, it should come back as 00 about half the time and 11 about half
the time -- and never 01 or 10. Any 01/10 outcome means something leaked:
a bad gate, a readout error, decoherence, a miswired circuit. So the check
is deliberately dumb: count the forbidden outcomes first, then look at the
split.

Usage:
    python3 bell_state_check.py results/bell-results.json

The JSON file is a list of runs. A run with full counts gets a computed
verdict; a run where only the outcome set was recorded (no exact split)
gets its recorded verdict reported as-is, flagged as partial -- the script
never invents counts it was not given.
"""

import json
import sys

FORBIDDEN = ("01", "10")
ALLOWED = ("00", "11")


def bell_circuit():
    """The circuit, as plain data: (gate, targets)."""
    return [
        ("H", [0]),
        ("CNOT", [0, 1]),
        ("MEASURE", [0, 1]),
    ]


def check_counts(counts):
    """Verdict for a run with full outcome counts.

    Returns a dict with the forbidden-outcome total, the 00/11 split,
    and a one-word verdict: 'clean' or 'dirty'.
    """
    forbidden = sum(counts.get(outcome, 0) for outcome in FORBIDDEN)
    total = sum(counts.values())
    split = {outcome: counts.get(outcome, 0) for outcome in ALLOWED}
    return {
        "shots": total,
        "forbidden_outcomes": forbidden,
        "split": split,
        "verdict": "clean" if forbidden == 0 else "dirty",
    }


def counts_for(run):
    """Outcome counts for a run, from full counts or recorded fractions.

    Fractions are scaled by shots and rounded; the recorded fractions are
    what the run notes actually kept, so the derived counts are flagged
    by the caller when they are used.
    """
    if "counts" in run:
        return run["counts"], False
    shots = run["shots"]
    return {
        outcome: round(frac * shots)
        for outcome, frac in run["fractions"].items()
    }, True


def describe(run):
    """One human-readable block per run in the results file."""
    lines = [
        f"Run: {run['backend']} -- {run.get('date', 'date not recorded')}",
        f"  result id: {run.get('result_id', 'not recorded')}",
    ]
    if "counts" in run or "fractions" in run:
        counts, derived = counts_for(run)
        result = check_counts(counts)
        split = result["split"]
        total = result["shots"] or 1
        lines.append(
            f"  shots: {result['shots']}, "
            f"00 = {split['00'] / total:.3f}, 11 = {split['11'] / total:.3f}, "
            f"forbidden (01/10) = {result['forbidden_outcomes']}"
        )
        lines.append(f"  verdict: {result['verdict']}")
        if derived:
            lines.append(
                "  (counts derived from the recorded fractions; "
                "the fractions are the primary record)"
            )
    else:
        # Partial record: only what was actually observed is claimed.
        lines.append(
            "  exact split not recorded -- only the outcome set was kept: "
            + ", ".join(run.get("observed_outcomes", []))
        )
        lines.append(
            f"  recorded verdict: {run.get('recorded_verdict', 'not recorded')} "
            "(partial record; counts not invented)"
        )
    if run.get("note"):
        lines.append(f"  note: {run['note']}")
    return "\n".join(lines)


def main(argv):
    if len(argv) != 2:
        print("usage: bell_state_check.py <results.json>", file=sys.stderr)
        return 2
    with open(argv[1]) as handle:
        runs = json.load(handle)
    print("Bell circuit: " + " -> ".join(
        f"{gate}{targets}" for gate, targets in bell_circuit()
    ))
    print()
    for run in runs:
        print(describe(run))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
