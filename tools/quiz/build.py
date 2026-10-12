"""Build quiz.json (what the site loads) from the candidates and the checks.

Only candidates that were checked and found OK are written. Prints what is still unchecked and
which questions have fewer than 3 good wrong answers (the quiz then shows fewer choices).

    python3 tools/quiz/build.py          # fails if anything is unchecked
    python3 tools/quiz/build.py --allow-unchecked
"""
import argparse
import datetime

import json

from quizlib import CANDIDATES, QUIZ, checks, load, pending_for


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--allow-unchecked", action="store_true")
    a = ap.parse_args()
    bank = load(CANDIDATES, None)
    if bank is None:
        raise SystemExit("run tools/quiz/candidates.py first")
    recs = checks()["questions"]
    out, unchecked, few = {}, [], []
    for q in bank["questions"]:
        rec = recs.get(q["id"])
        if pending_for(q, rec):
            unchecked.append(q["id"])
        good = [c for c in q["cands"] if rec and rec.get("text") == q["text"] and c[0] in rec.get("checked", [])
                and c[0] not in rec.get("bad", [])]
        if good:
            out[q["id"]] = good
        if len(good) < 3:
            few.append(f"{q['id']} ({len(good)})")
    with open(QUIZ, "w") as f:  # compact: the site downloads this file
        json.dump({"built": datetime.date.today().isoformat(), "questions": out}, f, ensure_ascii=False,
                  separators=(",", ":"), sort_keys=True)
    print(f"quiz.json: {len(out)} questions with checked wrong answers")
    if few:
        print(f"{len(few)} questions have fewer than 3 good wrong answers: {', '.join(few[:40])}{' ...' if len(few) > 40 else ''}")
    if unchecked:
        print(f"{len(unchecked)} questions still have unchecked candidates (run the quiz-check skill)")
        if not a.allow_unchecked:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
