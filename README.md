# Basic 1000

A step-by-step English course built on 1,000 basic words. Every definition uses only words from earlier steps.

Live site: https://basic-1000.vercel.app

## What's in this folder

| Path | What it is |
|---|---|
| `index.html` | The whole website: layout, lessons, quizzes, review, dictionary and Supabase sign-in |
| `grammar.js` | Grammar: the map of topics (a dependency tree), topic cards and lesson pages |
| `grammar-data.js` | The grammar curriculum and lessons, built from `content/grammar/` (do not edit by hand) |
| `films.js` | The stick-figure film player for grammar lessons |
| `content/grammar/` | `curriculum.py` (all 109 topics); full lessons (films, rules, exercises): `lessons.py` (Starting out) and `lessons_elem1-3.py` (Elementary school), written with the helpers in `lessons_kit.py` |
| `tools/grammar/build.py` | Checks the grammar content and writes `grammar-data.js` and the recording list |
| `figures.js` | Animated stick-figure scenes (D3), one per word; Units 1 and 2 (steps 1-20) so far |
| `audio.js` | Speaker buttons: plays each word and example (Daniel, or Sarah when a woman is speaking); slow buttons with highlighting |
| `pron.js` | IPA for the words with slow audio, split into sound groups (which letters spell which sound) |
| `lang.js`, `lang/` | Mother-language translations of the words: `lang/index.json` lists the languages, `lang/<code>.json` holds one language (built, do not edit by hand) |
| `content/lang/` | Translation sources: `languages.json` and one `<code>.tsv` per language |
| `tools/lang/build.py` | Checks the translations (every word, every language) and writes `lang/` |
| `quiz.json` | The checked wrong answers for every quiz question (see Quiz check) |
| `data-1.txt` ... `data-4.txt` | The 1,000 words the site loads (250 per file) |
| `content/course.json` | The full course data: steps, definitions, examples |
| `content/check_course.py`, `content/vocab.py` | Checks every course rule. Run after editing `course.json` |
| `tools/build_data.py` | Rebuilds the four data files from `content/course.json` |
| `supabase/migrations/` | Database table and security rules for saved progress; the public `audio` bucket |
| `supabase/functions/tts/index.ts` | Text-to-speech function: text + voice in, MP3 address out |
| `supabase/functions/backup/index.ts` | Backup function: copies the audio, the progress table and a code snapshot to Dropbox, keeping the newest 5 snapshots (see Backups) |
| `tools/tts-lab/lab_server.py` | Voice server for the GPU pod: Qwen3-TTS |
| `tools/quiz/` | Quiz check tools: makes sure every quiz question has only one right answer |
| `tools/audio_items.py` | Lists the clips a range of steps needs, as a request for the tts function |
| `tools/slow_items.py` | Lists the slow clips a range of steps needs, as a request for the tts function |
| `tools/pron/` | Builds `pron.js` (IPA and sound groups) from the CMU Pronouncing Dictionary plus hand entries |
| `content/jobs/` | Job lists the tts function reads from GitHub during a long audio run |
| `.vercelignore` | Keeps everything except the website files out of the Vercel deployment |

## Courses menu and grammar

The menu on the left (a strip at the top on phones) lists the courses: Basic 1000, Grammar, and Basic 2000 and Basic 3000, which are marked "Coming later" and cannot be opened yet. The Path, Review and Dictionary tabs belong to Basic 1000 and are hidden in Grammar.

### One site, not separate courses

The courses share one set of words and one progress record. Every word in a grammar rule, example, film subtitle or exercise answer is a link: touching it opens that word's page from Basic 1000 (the same card the Dictionary opens), which counts a visit, and from there the learner can jump to the word's step. Grammar progress is saved in the same record as everything else (`grammar` in the progress record), in the browser and in the learner's account.

### The curriculum

`content/grammar/curriculum.py` lists 109 topics in four bands: Starting out (10), Elementary school (36), Middle school (37) and High school (26). Each topic names the topics it needs first ("Past tense" needs "Verbs"), so together they form a dependency tree. Every word in every topic is one of the 1,000 words. A grammar word such as "noun" is not one of them, so the topic that first uses it gives it a meaning in basic words, and only that topic and the ones that build on it may use it.

`python3 tools/grammar/build.py` checks all of this: the words, the order (a topic always comes after the topics it needs, so there are no loops), that every Starting out and Elementary school topic has a full lesson with six well-formed exercises (the right answer is among the options, and so on), and that a woman's or girl's lines use Sarah's voice. It then writes `grammar-data.js` and `content/jobs/grammar_audio.json` (every sentence a lesson can say). Use `--check` to check only.

### The map

The Grammar page shows the tree: one section per band, each topic a card, with lines from each topic to the ones it opens. A topic is **done** (green tick), **open** (teal, ready to learn), **locked** (needs a topic that is not done yet), or **coming soon** (dashed, no lesson yet). Pointing at or touching a topic highlights everything it needs (yellow) and what it opens (teal). Touching opens a card with its goal, what to learn first, what comes after, and a button to start it. A locked topic can still be opened with "Look inside"; answers there are not saved. A coming-soon topic's card shows its rules and examples.

### A lesson

1. **Watch:** a narrated stick-figure film (`films.js`), 4-6 parts and about a minute long. Besides people and animals, films can show a table, chair, car, clock, moon, rain cloud, fish, bag, door, window, bottle, flower and fire. Words appear as tiles at the top and glide into new orders; colours show what each word is (noun, pronoun, verb, am/is/are, adjective). Lines are read by Daniel, or by Sarah when a woman or girl speaks. The bar under the film jumps to any part.
2. **The rule:** new grammar words with their meanings, the rule in short points, a table where it helps, and examples with listen buttons.
3. **Play** (some topics): the sentence machine. Pick who the sentence is about, then say it, say it with *not*, or ask it; the tiles glide so "is" visibly jumps to the front of a question.
4. **Try it:** six exercises: pick the right word, put the words in order (a word can be taken back by touching it, or with Undo, until Check is pressed), find and fix the wrong word, or touch every word of one kind. Getting 4 of 6 right finishes the topic and opens the topics under it.

### Recording the grammar sentences

Grammar sentences use the same clips as the rest of the site (`v2/{voice}/...` in the `audio` bucket). Until a sentence is recorded the browser's own voice reads it. To record new ones, commit `content/jobs/grammar_audio.json` and run the `batch` action with `list` pointing at it (chunk 16), as in the Audio section.

## How learners move through the course

- **One step at a time.** A step opens once every step before it is done, meaning its quiz has been taken. Locked steps show a padlock on the path; tapping one explains what opens it. Finished steps can always be opened again. The Dictionary stays open for every word; its "Open step" button is locked the same way.
- **Learning a word.** A word is learned when its four audio buttons are tapped in this order: the word, the word slowly, the first sentence, then the first sentence slowly.  At first only button 1 works. The others are grey and numbered, and the next one glows. A track at the top of the card shows the stops. "Next word" (or the step quiz) stays locked until the last tap. The word is then saved as learned (`learned` in the progress record), gets a "Learned" stamp and a teal top edge on its card, and its dot at the top of the lesson fills in. A learned word has no order: every button works straight away. Words from steps finished before this rule existed count as learned. A lesson always opens at the first word of its step that is not learned yet.
- **Visits.** Each time a learner opens a word's page (in a lesson, or from a tapped word or the Dictionary), its visit count goes up by one. The count is shown next to the word, with five bars that fill at 1, 3, 5, 10 and 20 visits. Counts are part of the learner's progress (`views` in the saved record), so they are kept in the browser and in their account when signed in. When two devices are merged, the higher count is kept.

- **Mother language.** Every word shows a short translation in the learner's own language, under the word on its page and in the Dictionary (which can also be searched in that language). It gives the meaning the word's example sentences teach. Sentences are not translated, and quiz questions never show translations. The default is English only (no translation: learn English through English); the globe button in the header turns on one of ten languages: the top 10 of [Ethnologue](https://www.ethnologue.com/insights/ethnologue200/)'s 2025 ranking by total speakers other than English itself (Chinese, Hindi, Spanish, Arabic, French, Bengali, Portuguese, Russian, Indonesian) plus German. Arabic is shown right to left; Dictionary search works in every script (from one character for scripts like Chinese, from three letters for Latin letters). The choice is saved in the progress record (`ml`, with the time it was made in `mlt`; when two devices are merged, the later choice wins).

### Adding a language

1. Write `content/lang/<code>.tsv`: one line per word, `word<TAB>translation`, in the sense the examples teach. Several senses are separated by `; `, the one in the first example first.
2. Add `{ "code", "name" (in that language), "english" }` to `content/lang/languages.json`, plus `"dir": "rtl"` for a right-to-left script and `"tag"` when the language tag differs from the code (for example `"tag": "zh-Hans"`). The order of the list is the order in the picker.
3. Run `python3 tools/lang/build.py`. It refuses a missing, extra or empty word. The site needs no change.

## Editing the course

1. Edit `content/course.json` (through `tools/pipeline/src/`, see `CLAUDE.md`). New words also need a line in every `content/lang/<code>.tsv`.
2. Run `python3 content/check_course.py` and fix anything it reports.
3. Run `python3 tools/build_data.py` to rebuild the data files.
4. Run the quiz check (see Quiz check below) so new questions get checked wrong answers.
5. Deploy.

## Deploying

From this folder: `npx vercel --prod` (Vercel project `basic-1000`). Only the website files in the top folder are uploaded (`.vercelignore` keeps `content`, `tools` and `supabase` out). Pushing to `main` on GitHub (`johnlqdev/basic1000`) does not deploy by itself: start a production deployment from the pushed commit (Vercel dashboard, or the Vercel API with the commit SHA).

## Backups

Code and course content are in GitHub. Everything else is copied to Dropbox by the `backup` edge function, into one folder: `basic1000-backup/` inside the Dropbox app's folder. Nothing outside that folder is touched.

- `audio/`: one copy of every file in the `audio` storage bucket, path for path (word and sentence clips, slow clips and their timing, and `refs/`, the reference recordings that define Daniel's and Sarah's voices). New and changed files are added; nothing is duplicated, so it takes the bucket's size once (about 310 MB).
- `snapshots/<date>/`: `progress.json` (the learners' saved progress) and `basic1000-<commit>.zip` (the GitHub repo at that commit), about 1 MB each week. Only the newest 5 snapshots are kept; older ones are deleted.
- `manifest.json`: what is there, when it was written, and how to restore.

**Schedule** (pg_cron in the database, migration `0004_backup_schedule.sql`): every Sunday at 03:17 Singapore time a snapshot, one batch of audio and the manifest; every day at 03:37 any new or changed audio (up to 700 files; when nothing changed it costs one database query). Results are in `net._http_response`; the jobs are listed in `cron.job`.

The `backup_log` table remembers which storage files are copied. To run by hand from SQL with the admin token (as for the tts function): `{"action":"all"}`, `{"action":"snapshot"}`, `{"action":"audio","limit":700}` (repeat until `pending` is 0) or `{"action":"status"}`. Secrets `DROPBOX_APP_KEY`, `DROPBOX_APP_SECRET` and `DROPBOX_REFRESH_TOKEN` are set in the Supabase dashboard. Secrets themselves are not backed up: keep them in a password manager.

## Services

- **Vercel** project `basic-1000`, free Hobby plan (non-commercial use).
- **Supabase** project `basic-1000` (Singapore). The site uses only the public publishable key; the security rules let each signed-in learner read and write only their own progress row.

## Audio

Every word and example sentence has a speaker button. The voices come from **Qwen3-TTS 1.7B** (Alibaba, open source, Apache-2.0), all American English:

- **Daniel** (`us_daniel`) reads every word and every neutral sentence.
- **Sarah** (`us_sarah`) reads a sentence only when a woman must be the speaker ("I am a woman.", "I am not a man."). The rule is `voiceFor()` in `audio.js` and `voice_for()` in `tools/audio_items.py`; keep them the same.
- Every step has its clips: each word and both of its example sentences.

How it works:

- Daniel and Sarah are designed voices: the model read one sentence from a written description (see `VOICE_SPECS` in the tts function), and that recording is kept at `refs/qwen_daniel.wav` and `refs/qwen_sarah.wav` in the `audio` bucket. Every clip is cloned from it, so they sound the same in every session. Do not delete those two files.
- Every clip is made once and kept in the public Supabase bucket `audio`, at `v2/{voice}/{first 32 hex of sha256(voice + "|" + text)}.mp3`. The site works out that address itself, so stored clips play with no server call.
- Every clip has 0.5 s of silence before the voice and 0.4 s after (`supabase/functions/tts/pad.ts`), so the first word is not swallowed while speakers wake up.
- Ask for any text: `GET https://duptugctgzemfczbtvgj.supabase.co/functions/v1/tts?text=I%20am%20a%20woman.&voice=woman` returns `{ "url": ... }` (`voice=man` is Daniel, `voice=woman` is Sarah). A new text is made only while the pod is running; otherwise the reply is 503 and the site falls back to the browser's own voice.
- Admin actions need the `x-admin-token` header (the token is in the Supabase vault as `tts_admin_token`): `status`, `start`, `stop`, `batch`, `pods`, `create`, `delete`. The function reads the RunPod key from the Supabase secret `RUNPOD_API_KEY`.
- The GPU pod `basic1000-lab` runs `tools/tts-lab/lab_server.py` (downloaded from GitHub at a fixed commit when the pod is created). It loads in about a minute and makes about 32 clips in 3 seconds. About $0.89 an hour on an RTX 4090 while running; nothing while stopped. If it will not start ("not enough free GPUs"), delete it and create it again: the stored references keep the voices the same. Create it with `"volumeInGb": 0` and delete it (not only stop it) when the audio is done: a stopped pod costs nothing, but a volume keeps billing (RunPod adds 20 GB if the spec leaves it out).

To make audio for new words (for example a second thousand):

1. Start the pod: `{"action":"start","pod":"lab"}`, then wait until `status` shows the server is ready.
2. Write the job list, for example `python3 tools/audio_items.py 201 400 > content/jobs/normal.json`, and push it to GitHub. Then send `{"action":"batch","chunk":32,"compact":true,"list":"https://raw.githubusercontent.com/johnlqdev/basic1000/<commit>/content/jobs/normal.json","offset":0,"count":160}`, raising `offset` by 160 each time. Clips already made are skipped.
3. Stop the pod: `{"action":"stop","pod":"lab"}`.
4. Make the slow clips (below), then raise `MAX_STEP` and `SLOW_MAX_STEP` in `audio.js` and deploy.

The voice trial clips (16 Qwen voices for steps 1-5, and the older Kokoro clips) are still in storage but no longer used.

### Slow buttons

Next to each speaker button is a tortoise button. It plays the same recording slowed down, with the pitch unchanged: words at 60 % speed, sentences at 70 %. While it plays:

- **Words:** the headword's letters and its IPA (shown under the headword) light up one sound at a time. "woman" lights up w, o, m, a, n and, underneath, /ˈw/, /ʊ/, /m/, /ə/, /n/.
- **Sentences:** each word lights up while it is read.

How it is made:

- `pron.js` has the IPA for each word, split into sound groups such as `['ou', 'aʊ']` (the letters "ou" spell /aʊ/). It is made by `python3 tools/pron/build_pron.py cmudict.dict --review` from the CMU Pronouncing Dictionary (https://github.com/cmusphinx/cmudict, BSD licence): the first pronunciation of each word, with its letters lined up with its sounds using the common spellings in `tools/pron/spellings.py`. Hand entries in `tools/pron/overrides.json` win; they cover the first 25 words, homographs taught in another sense (live /lɪv/, read /rid/, lead /lid/, wind /wɪnd/, close /kloʊz/, the noun record), and a few odd spellings. The IPA follows what Daniel says when he reads the word alone, so "a" is /eɪ/ and "the" is /ði/.
- The voice server (`tools/tts-lab/lab_server.py`, `/slow_batch`) takes the stored normal clip and slows it down with Rubber Band (through ffmpeg). It then finds when each letter is heard with forced alignment, using `facebook/wav2vec2-large-960h-lv60-self`. It also writes down what a phoneme model (`facebook/wav2vec2-lv-60-espeak-cv-ft`) hears, as `heard`, which was used to check the IPA.
- The tts function's admin action `slow` stores two files next to the normal clip: `slow1/{voice}/{same name}.mp3` and `.json`, the timing file. The page lights each sound from the moment the aligner marks until halfway to the next one. If a slow clip is missing, the page plays the normal clip slowed down by the browser, without highlighting.

To add slow buttons for new words:

1. Run `tools/pron/build_pron.py` again and check its `--review` list, adding overrides where needed. A group's letters must spell the word exactly; silent letters join a neighbouring group.
2. Write `python3 tools/slow_items.py 201 400 > content/jobs/slow.json`, push it, start the pod and send `{"action":"slow","chunk":10,"compact":true,"list":"…/content/jobs/slow.json","offset":0,"count":100}` until done. The report lists words whose IPA does not match what the phoneme model heard (`flagged`); check those, then stop the pod.
3. Raise `SLOW_MAX_STEP` in `audio.js` and deploy.

## Quiz check

A quiz question must have exactly one right answer. "___ is a girl." with both "this" and "that" among the choices is a broken question, because both make a good sentence.

So the quizzes never pick wrong answers at random. Every question the site can ask has a fixed list of candidate wrong answers, and each candidate is checked by hand: it is **bad** if it would also give a sentence that is grammatical and makes sense (or, for a meaning question, if the word also fits the meaning). The site loads `quiz.json` and offers only candidates that were checked and found to be wrong. A sentence where almost any word fits ("What is the ___?") gives way to another sentence or to the meaning question.

| File | What it is |
|---|---|
| `content/quiz_candidates.json` | Every question with its candidate wrong answers (made by `candidates.py` from the site itself) |
| `content/quiz_checks.json` | The verdicts: for each question, which candidates were checked (the "checked" flag) and which were bad |
| `quiz.json` | What the site loads: the good wrong answers for each question |
| `tools/quiz/` | The tools below |

Run the check after every change to the course (new words, new or edited sentences):

```
python3 tools/quiz/candidates.py      # list every question and its candidates
python3 tools/quiz/pending.py --count # how many still need a verdict
python3 tools/quiz/pending.py         # show the next 120, then write the bad ones to a file
python3 tools/quiz/record.py verdicts.txt
# repeat candidates.py, pending.py, record.py until pending.py --count says 0
python3 tools/quiz/build.py           # write quiz.json, then deploy
```

The check is incremental: a candidate that was already checked is never shown again, so adding the next 1,000 words means checking only the new questions (and old ones whose sentence changed). The `quiz-check` skill runs these steps.
