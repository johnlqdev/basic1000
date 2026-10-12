"""Record verdicts for the chunk last shown by pending.py.

Give only the BAD candidates (ones that would also be right), one question per line:

    g:this:0: that, it
    d:girl: child

Every other candidate in the chunk is recorded as checked and OK.

    python3 tools/quiz/record.py verdicts.txt        # or: ... | python3 tools/quiz/record.py -
"""
import datetime
import re
import sys

from quizlib import CHECKS, PENDING, RULE, checks, load, save


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "-"
    text = sys.stdin.read() if src == "-" else open(src).read()
    chunk = load(PENDING, None)
    if not chunk:
        raise SystemExit("no pending chunk; run tools/quiz/pending.py first")
    items = {t["id"]: t for t in chunk["items"]}
    bad = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^(g:.+:\d+|d:[^:]+):\s*(.*)$", line)
        if not m:
            raise SystemExit(f"cannot read line: {line!r}")
        qid, rest = m.group(1).strip(), m.group(2).strip()
        if qid not in items:
            raise SystemExit(f"not in the current chunk: {qid!r}")
        labels = [x.strip() for x in rest.split(",") if x.strip() and x.strip() != "-"]
        unknown = [x for x in labels if x not in items[qid]["labels"]]
        if unknown:
            raise SystemExit(f"{qid}: {unknown} are not candidates of this question")
        bad[qid] = labels
    data = checks()
    data["rule"] = RULE
    today = datetime.date.today().isoformat()
    for qid, t in items.items():
        rec = data["questions"].get(qid)
        if not rec or rec.get("text") != t["text"] or rec.get("answer") != t["answer"]:
            rec = {"text": t["text"], "answer": t["answer"], "checked": [], "bad": []}
        rec["checked"] = sorted(set(rec["checked"]) | set(t["labels"]))
        rec["bad"] = sorted(set(rec["bad"]) | set(bad.get(qid, [])))
        rec["date"] = today
        data["questions"][qid] = rec
    save(CHECKS, data)
    save(PENDING, {"items": []})
    print(f"recorded {len(items)} questions, {sum(len(v) for v in bad.values())} bad candidates")


if __name__ == "__main__":
    main()
