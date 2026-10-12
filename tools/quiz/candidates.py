"""List every quiz question and its candidate wrong answers -> content/quiz_candidates.json.

Each question gets N_CANDIDATES candidates; if the checks found too many of them to be right answers
too, more are added (up to N_MAX) so that the quiz can still show three wrong answers.

The list comes from the site itself (window.BASIC1000_QUIZ_BANK in index.html), so it uses exactly the
same word forms and rules as the quizzes. Run it after changing the course data.

    python3 tools/quiz/candidates.py
"""
import functools
import http.server
import os
import threading

from quizlib import CANDIDATES, GOOD_TARGET, N_CANDIDATES, N_MAX, ROOT, checks, save

D3_LOCAL = "/opt/npm-tools/node_modules/d3/dist/d3.min.js"  # optional offline copy of d3


def main():
    from playwright.sync_api import sync_playwright
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    handler = functools.partial(Quiet, directory=ROOT)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        if os.path.exists(D3_LOCAL):
            page.route("https://cdnjs.cloudflare.com/ajax/libs/d3/**",
                       lambda r: r.fulfill(path=D3_LOCAL, content_type="application/javascript"))
        page.route("https://cdn.jsdelivr.net/**", lambda r: r.abort())
        page.route("https://fonts.googleapis.com/**", lambda r: r.abort())
        page.route("**/quiz.json", lambda r: r.fulfill(status=404, body=""))
        page.goto(f"http://127.0.0.1:{server.server_address[1]}/")
        page.wait_for_function("typeof window.BASIC1000_QUIZ_BANK === 'function'", timeout=30000)
        bank = page.evaluate(f"window.BASIC1000_QUIZ_BANK({N_MAX})")
        browser.close()
    server.shutdown()
    # keep the first N_CANDIDATES; add more only where earlier checks found too many of them bad
    recs = checks()["questions"]
    for q in bank:
        rec = recs.get(q["id"])
        bad = set(rec.get("bad", [])) if rec and rec.get("text") == q["text"] else set()
        n = N_CANDIDATES
        while n < len(q["cands"]) and sum(c[0] not in bad for c in q["cands"][:n]) < GOOD_TARGET:
            n += 1
        q["cands"] = q["cands"][:n]
    bank = sorted(bank, key=lambda q: q["id"])
    save(CANDIDATES, {"n": N_CANDIDATES, "questions": bank})
    gaps = sum(q["kind"] == "gap" for q in bank)
    print(f"{len(bank)} questions ({gaps} gap, {len(bank) - gaps} meaning), "
          f"{sum(len(q['cands']) for q in bank)} candidates -> {os.path.relpath(CANDIDATES, ROOT)}")


if __name__ == "__main__":
    main()
