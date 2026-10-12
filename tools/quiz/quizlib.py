"""Shared paths and helpers for the quiz-check tools (see "Quiz check" in README.md)."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CANDIDATES = os.path.join(ROOT, "content", "quiz_candidates.json")  # every question + its candidate wrong answers
CHECKS = os.path.join(ROOT, "content", "quiz_checks.json")          # the verdicts (the "checked" flags)
QUIZ = os.path.join(ROOT, "quiz.json")                               # what the site loads
PENDING = os.path.join(ROOT, "content", "quiz_pending.json")         # the chunk currently being reviewed
N_CANDIDATES = 6  # candidate wrong answers listed per question; the quiz shows 3 of the ones that pass
N_MAX = 16        # when too many of the 6 turn out to be right answers too, more are added, up to this many
GOOD_TARGET = 4   # ... until at least this many are not known to be bad

RULE = ("A candidate is BAD when putting it in the gap gives a sentence that is grammatical and makes sense "
        "(so it would also be a right answer), or, for a meaning question, when the word also fits the meaning. "
        "Everything else is OK (ungrammatical, or plainly nonsense such as 'He is a girl.'). When in doubt: BAD.")


def load(path, default):
    if not os.path.exists(path):
        return default
    with open(path) as f:
        return json.load(f)


def save(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=1, ensure_ascii=False, sort_keys=True)
        f.write("\n")


def checks():
    return load(CHECKS, {"rule": RULE, "questions": {}})


def pending_for(q, rec):
    """Candidate labels of question q that still need a verdict, given its check record (or None)."""
    if not rec or rec.get("text") != q["text"] or rec.get("answer") != q["answer"]:
        return [c[0] for c in q["cands"]]  # never checked, or the sentence / answer changed: check all again
    done = set(rec.get("checked", []))
    return [c[0] for c in q["cands"] if c[0] not in done]
