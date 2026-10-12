"""Show the next chunk of quiz candidates that still need a verdict, and remember it for record.py.

    python3 tools/quiz/pending.py            # next 120 questions
    python3 tools/quiz/pending.py --limit 60
    python3 tools/quiz/pending.py --count    # only how many are left

Each line:  <id> | <sentence with ___, or MEANING: definition> | right: <answer> | <candidates to judge>
"""
import argparse

from quizlib import CANDIDATES, PENDING, checks, load, pending_for, save


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=120)
    ap.add_argument("--count", action="store_true")
    a = ap.parse_args()
    bank = load(CANDIDATES, None)
    if bank is None:
        raise SystemExit("run tools/quiz/candidates.py first")
    recs = checks()["questions"]
    todo = []
    for q in bank["questions"]:
        labels = pending_for(q, recs.get(q["id"]))
        if labels:
            todo.append({"id": q["id"], "text": q["text"], "answer": q["answer"], "labels": labels,
                         "kind": q["kind"], "prompt": q["prompt"]})
    if a.count:
        print(f"{len(todo)} questions still need checking ({sum(len(t['labels']) for t in todo)} candidates)")
        return
    chunk = todo[: a.limit]
    save(PENDING, {"items": chunk})
    for t in chunk:
        shown = t["prompt"] if t["kind"] == "gap" else "MEANING: " + t["prompt"]
        print(f"{t['id']} | {shown} | right: {t['answer']} | {', '.join(t['labels'])}")
    print(f"-- {len(chunk)} of {len(todo)} pending questions shown; saved for record.py")


if __name__ == "__main__":
    main()
