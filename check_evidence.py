#!/usr/bin/env python3
"""
check_evidence.py — Lit evidence.json et affiche un résumé des preuves du TP.

Usage :
    python3 check_evidence.py
"""

import json
import sys
from pathlib import Path

EVIDENCE_FILE = Path(__file__).parent / "evidence.json"

VERDICT_ICONS = {
    "PASS": "✅",
    "DENY": "✅",   # un DENY attendu et observé est un succès du test
    "FAIL": "❌",
    "PENDING": "⏳",
}


def load_evidence(path: Path) -> list[dict]:
    if not path.exists():
        print(f"Erreur : fichier introuvable ({path})")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    tests = load_evidence(EVIDENCE_FILE)

    print(f"{'Test':45} {'Attendu':30} {'Verdict':10}")
    print("-" * 90)

    counts = {"PASS": 0, "DENY": 0, "FAIL": 0, "PENDING": 0}

    for t in tests:
        verdict = t.get("verdict", "PENDING")
        icon = VERDICT_ICONS.get(verdict, "?")
        counts[verdict] = counts.get(verdict, 0) + 1
        print(f"{t['test'][:45]:45} {t['attendu'][:30]:30} {icon} {verdict}")

    print("-" * 90)
    total = len(tests)
    done = counts["PASS"] + counts["DENY"] + counts["FAIL"]
    print(f"\n{done}/{total} tests renseignés — "
          f"{counts['PASS'] + counts['DENY']} réussis, "
          f"{counts['FAIL']} échoués, "
          f"{counts['PENDING']} en attente.")

    if counts["FAIL"] > 0:
        print("\n⚠️  Des tests sont en échec — voir le détail ci-dessus.")
        sys.exit(1)


if __name__ == "__main__":
    main()
