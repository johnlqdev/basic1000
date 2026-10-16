# Basic 1000 — rule book

Standing rules for all work on this project. Read this first, and follow it for every piece of new
content (words, examples, grammar, videos, audio). The owner sets these rules; add new ones here
when the owner gives them, with the date.

## Content

1. **First example = plain form.** (2026-10-14) The first example sentence of every word uses the
   word exactly as it is written in the list: "I make a cake.", not "I made a cake." / "She makes a
   cake."; "A cow gives milk.", not "Cows give milk.". No past tense, no -s, no -ing, no plural for
   the headword itself. The first example must also be usable at the word's own step. Other words in
   the sentence may take any form. Enforced by `content/check_course.py` (rule 4).
2. **Only known words.** A definition uses only words from earlier steps; an example uses only words
   from earlier steps or the same step (`content/check_course.py`). Grammar lessons use only the
   1,000 words, plus terms defined by the node or its ancestors (`tools/grammar/build.py --check`).
3. **The step order is pinned** (`tools/pipeline/order_pinned.json`). Audio, pictures and films are
   made per step, so editing a sentence must never move words between steps.
4. **Edit the pipeline source, not only course.json.** Sentences live in `tools/pipeline/src/b*.txt`;
   rebuild with `tools/pipeline/build_course.py`, copy `out/course.json` to `content/`, then run
   `python3 tools/build_data.py`.
5. **Every quiz question has exactly one right answer.** After changing words or examples, run the
   quiz-check steps (`tools/quiz/`, see the quiz-check skill) until nothing is pending.
6. **Videos follow the first example.** A word's scene in `figures.js` acts out its first example and
   shows the same sentence. If the sentence changes, change the scene.
7. **Modules are linked.** Every word shown in grammar (examples, rules, answers) links to its
   Basic 1000 word page and counts as a visit.
8. **Mother-language annotations.** (2026-10-14) Every word has a short, intuitive translation in
   every listed language, in the meaning its example
   sentences teach (several senses: "; ", the first example's sense first). Words only, never
   sentences, and never shown in quiz questions. Sources: `content/lang/<code>.tsv` plus
   `content/lang/languages.json`; build with `python3 tools/lang/build.py` (writes `lang/`). A new
   word needs its translation in every language; if a word's first example changes meaning, check
   its translations. Adding a language = one new `.tsv` + one line in `languages.json`.
   The default is English only (no translation shown: learn English through English). Options
   (2026-10-14): the top 10 languages of Ethnologue 2025 by total speakers other than English —
   Chinese (Simplified), Hindi, Spanish, Arabic, French, Bengali, Portuguese, Russian, Indonesian —
   plus German. Right-to-left scripts set `"dir": "rtl"`; a language tag that differs from the code
   goes in `"tag"` (e.g. `zh-Hans`).

9. **Words talked about go in curly quotes.** (2026-10-15) When a grammar text talks about a word
   instead of using it, put it in “curly quotes”: "“We” is you and other people.", "For an animal,
   we say “it”.". Unquoted, the voice reads it as a normal word: no stress, and short words lose
   their last sound or come out wrong ("am"). A sentence that starts with a quoted word (or list) is
   read with a comma after it, so the voice stresses it and pauses before the verb; `say_text()` in
   `tools/grammar/build.py` adds that comma to the audio job only (`say`), never to the shown text.
   `build.py --check` fails on the usual slips ("We is ...", "And adds ...", "we say it."), but it
   cannot see every case: read each new narration line and ask "is this word used, or talked about?"
   The same goes for any new text the voice reads, not only grammar.

## Audio

- Voices: Daniel (`man`) by default; Sarah (`woman`) only when a woman is speaking
  (`voice_for` in `tools/audio_items.py`, `voiceFor` in `audio.js`).
- A single word is read as "Word." (`spoken()` in the tts function), so its last sound is not lost.
- Every new sentence needs a normal clip and, for course examples, a slow clip. When the audio is
  done, **delete** the GPU pod (2026-10-14). Create it with `"volumeInGb": 0`: RunPod otherwise adds a
  20 GB volume that bills about $0.01/h even while the pod is stopped. Nothing on the pod needs
  keeping (the voice references are in Supabase storage, the server is downloaded at start).
- If clips are made again under the same name, raise `FRESH` in `audio.js` (clips are cached for a
  year).
- **Check new audio before shipping** (2026-10-15). The owner should not be the one who finds a
  swallowed sound. After recording, run the tts `slow` action at `tempo: 1` on the sentences that
  matter and read `heard` (the phonemes heard) and the word timings: short words and words at the
  end of a sentence must be heard whole (the final "k" of "make", the "t" of "it"), and a quoted
  first word needs a clear pause before the next word (about 0.5 s; unquoted it was 0.2 s).
- **A clip with the same name is never replaced on its own.** `batch` skips any text that already
  has a clip, including test clips made while trying things. When a sentence must be re-recorded
  (new `say`, new voice rule), send it with `force: true`.
- **List the pods before creating one, and again at the end** (2026-10-16). The tts function finds
  its pod by name (`basic1000-lab`), so a second pod with the same name, say one left by an
  interrupted session, keeps billing unseen and `delete` removes only one of them. Reuse or delete
  any `basic1000-*` pod first; at the end, check that none is left.
- **Check every sentence, not a sample** (2026-10-16). Run the phoneme check on every new or
  changed sentence and compare `heard` word by word, above all the word being taught or talked
  about. Misreads found so far: a quoted "am" heard as "arm" or "A.M."; "I am a man." with the weak
  "əm"; one take of “These” heard as "this". The word a lesson teaches must be said in its full,
  clear form.
- **Fix a misread in the spoken text, never in the shown text.** In `tools/grammar/build.py`:
  `SAY_SPELLING` respells a word for the voice everywhere (“am” → “Amm”), and a film line can carry
  its own `say` (`L('I am a man.', say='I AM a man.')`). Try a few wordings on test names
  (`text: "zz test 1"` plus `say`), take one that is heard right twice, then record and check the
  real clip. The voice is not always right even then: check the real clip and redo it if needed.
- **Words must not run together** (2026-10-16). Read the word timings too: between a quoted word and
  what follows (above all at a colon before examples), there should be a clear pause (0.3 s or
  more). "we add “es”: box, boxes." had 0.12 s and sounded like "eezbox"; it is now said
  "we add “E S”... Box, boxes." (0.46 s). An ending such as "es" or "ed" is spelled out as
  letters, the way the voice already reads "s".
- **The same wording gives the same take.** Recording a sentence again with the same `say` returns
  the same audio, so to get a different take, change the wording a little (a comma, say).
- **Make sure you are checking the new clip.** The `slow` check reads the clip through the CDN,
  which can serve the old copy for a while after an overwrite. Before checking, compare the `head`
  size of the clip's URL with and without `?x=<time>`; check only once they are the same (about
  75 s).

## Grammar videos (MP4)

- (2026-10-15) The 46 grammar films also exist as MP4s in Dropbox `basic1000-backup/grammar-videos/`
  (`grammar_46_phone.zip`, `grammar_46_desktop.zip`), made by `tools/video/` from the site's own data
  and clips. **When a film's text, pictures or audio change, make both sets again and replace both
  zips** in the same piece of work: 46 videos in each, all with sound, checked to use the new clips.
- **Every word in quotes has a yellow background** (2026-10-16), in the videos (`subHTML` in
  `tools/video/frame.html`) and in the site's films (`markQuoted` in `films.js`), together with the
  words a line marks itself (`hl`).
- **Subtitles must read well in both sizes** (2026-10-16). A long line wraps as one paragraph over
  as many lines as it needs, with a quoted word or phrase kept on one line. `render.py` checks
  every subtitle in every layout before it records, and stops when one does not fit; also look at
  frames of the longest lines in the phone layout. Video styles live in `tools/video/frame.html` and
  must not reuse the site's class names: `.q`, the site's quiz card, once put a white card around
  speech lines that ran off the phone screen.
- The videos are made on a pod (README, "Grammar videos"). If no CPU pod is free, use a GPU pod with
  the `pytorch/pytorch` image (the Playwright image never started on a GPU host) and install
  Playwright and Chromium there. Delete the pod when the zips are checked.
- `public.pod_cmds` and `public.pod_runs` are shared with other projects: read and write only rows
  of this project's own run (filter by `run_id`). Never touch other projects' pods.

## Safety and secrets

- Never print or paste API keys, tokens or passwords. The admin token lives in the Supabase vault
  (`tts_admin_token`). Never put the Supabase service role key in the site; only the publishable key.
- The owner adds secrets in the Supabase dashboard (RUNPOD_API_KEY, DROPBOX_*).
- Dropbox: write only inside `basic1000-backup/`. Never touch the other folders in the app folder.

## Shipping

- Commit as "Basic 1000" <noreply@anthropic.com>. Pushing does not deploy: create a Vercel
  production deployment for the commit and wait until it is READY.
- Before shipping content: `python3 content/check_course.py`, `python3 tools/grammar/build.py --check`,
  `python3 tools/lang/build.py --check`.
