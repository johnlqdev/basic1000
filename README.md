# Basic 1000

A step-by-step English course built on 1,000 basic words. Every definition uses only words from earlier steps.

Live site: https://basic-1000.vercel.app

## What's in this folder

| Path | What it is |
|---|---|
| `index.html` | The whole website: layout, lessons, quizzes, review, dictionary and Supabase sign-in |
| `figures.js` | Animated stick-figure scenes (D3), one per word; all of Unit 1 (steps 1-10) so far |
| `audio.js` | Speaker buttons: plays each word and example (Daniel, or Sarah when a woman is speaking); slow buttons with highlighting |
| `pron.js` | IPA for the words with slow audio, split into sound groups (which letters spell which sound) |
| `quiz.json` | The checked wrong answers for every quiz question (see Quiz check) |
| `data-1.txt` ... `data-4.txt` | The 1,000 words the site loads (250 per file) |
| `content/course.json` | The full course data: steps, definitions, examples |
| `content/check_course.py`, `content/vocab.py` | Checks every course rule. Run after editing `course.json` |
| `tools/build_data.py` | Rebuilds the four data files from `content/course.json` |
| `supabase/migrations/` | Database table and security rules for saved progress; the public `audio` bucket |
| `supabase/functions/tts/index.ts` | Text-to-speech function: text + voice in, MP3 address out |
| `tools/tts-lab/lab_server.py` | Voice server for the GPU pod: Qwen3-TTS |
| `tools/quiz/` | Quiz check tools: makes sure every quiz question has only one right answer |
| `tools/audio_items.py` | Lists the clips a range of steps needs, as a request for the tts function |
| `tools/slow_items.py` | Lists the slow clips a range of steps needs, as a request for the tts function |
| `.vercelignore` | Keeps everything except the website files out of the Vercel deployment |

## How learners move through the course

- **One step at a time.** A step opens once every step before it is done, meaning its quiz has been taken. Locked steps show a padlock on the path; tapping one explains what opens it. Finished steps can always be opened again. The Dictionary stays open for every word; its "Open step" button is locked the same way.
- **Learning a word.** A word is learned when its learning buttons are tapped in this order: the word, the word slowly, "Watch from the start" (under the picture, it replays the scene), the first sentence, then the first sentence slowly. Only the buttons the word has count; steps 6-10 have no slow buttons yet. At first only button 1 works. The others are grey and numbered, and the next one glows. A track at the top of the card shows the five stops. "Next word" (or the step quiz) stays locked until the last tap. The word is then saved as learned (`learned` in the progress record), gets a "Learned" stamp and a teal top edge on its card, and its dot at the top of the lesson fills in. A learned word has no order: every button works straight away. Words with nothing to tap yet (from step 11, which has no audio or pictures) count as learned when opened. Words from steps finished before this rule existed count as learned. A lesson always opens at the first word of its step that is not learned yet.
- **Visits.** Each time a learner opens a word's page (in a lesson, or from a tapped word or the Dictionary), its visit count goes up by one. The count is shown next to the word, with five bars that fill at 1, 3, 5, 10 and 20 visits. Counts are part of the learner's progress (`views` in the saved record), so they are kept in the browser and in their account when signed in. When two devices are merged, the higher count is kept.

## Editing the course

1. Edit `content/course.json`.
2. Run `python3 content/check_course.py` and fix anything it reports.
3. Run `python3 tools/build_data.py` to rebuild the data files.
4. Run the quiz check (see Quiz check below) so new questions get checked wrong answers.
5. Deploy.

## Deploying

From this folder: `npx vercel --prod` (Vercel project `basic-1000`). Only `index.html`, `figures.js`, `audio.js`, `quiz.json` and the data files are uploaded. Pushing to `main` on GitHub (`johnlqdev/basic1000`) also deploys.

## Services

- **Vercel** project `basic-1000`, free Hobby plan (non-commercial use).
- **Supabase** project `basic-1000` (Singapore). The site uses only the public publishable key; the security rules let each signed-in learner read and write only their own progress row.

## Audio

Every word and example sentence has a speaker button. The voices come from **Qwen3-TTS 1.7B** (Alibaba, open source, Apache-2.0), all American English:

- **Daniel** (`us_daniel`) reads every word and every neutral sentence.
- **Sarah** (`us_sarah`) reads a sentence only when a woman must be the speaker ("I am a woman.", "I am not a man."). The rule is `voiceFor()` in `audio.js` and `voice_for()` in `tools/audio_items.py`; keep them the same.
- Unit 1 (steps 1-10) has all its clips: 135 by Daniel, 2 by Sarah. `MAX_STEP` in `audio.js` sets how many steps show buttons; later steps say "Audio for this step is coming soon".

How it works:

- Daniel and Sarah are designed voices: the model read one sentence from a written description (see `VOICE_SPECS` in the tts function), and that recording is kept at `refs/qwen_daniel.wav` and `refs/qwen_sarah.wav` in the `audio` bucket. Every clip is cloned from it, so they sound the same in every session. Do not delete those two files.
- Every clip is made once and kept in the public Supabase bucket `audio`, at `v2/{voice}/{first 32 hex of sha256(voice + "|" + text)}.mp3`. The site works out that address itself, so stored clips play with no server call.
- Every clip has 0.5 s of silence before the voice and 0.4 s after (`supabase/functions/tts/pad.ts`), so the first word is not swallowed while speakers wake up.
- Ask for any text: `GET https://duptugctgzemfczbtvgj.supabase.co/functions/v1/tts?text=I%20am%20a%20woman.&voice=woman` returns `{ "url": ... }` (`voice=man` is Daniel, `voice=woman` is Sarah). A new text is made only while the pod is running; otherwise the reply is 503 and the site falls back to the browser's own voice.
- Admin actions need the `x-admin-token` header (the token is in the Supabase vault as `tts_admin_token`): `status`, `start`, `stop`, `batch`, `pods`, `create`, `delete`. The function reads the RunPod key from the Supabase secret `RUNPOD_API_KEY`.
- The GPU pod `basic1000-lab` runs `tools/tts-lab/lab_server.py` (downloaded from GitHub at a fixed commit when the pod is created). It loads in about a minute and makes about 32 clips in 3 seconds. About $0.89 an hour on an RTX 4090 while running; nothing while stopped. If it will not start ("not enough free GPUs"), delete it and create it again: the stored references keep the voices the same.

To add audio for more steps (for example 11-20):

1. Start the pod: `{"action":"start","pod":"lab"}`, then wait until `status` shows the server is ready.
2. Send the output of `python3 tools/audio_items.py 11 20` as a `batch` request (about 60 items per call, so each call finishes within the time limit).
3. Stop the pod: `{"action":"stop","pod":"lab"}`.
4. Raise `MAX_STEP` in `audio.js` and deploy.

The voice trial clips (16 Qwen voices for steps 1-5, and the older Kokoro clips) are still in storage but no longer used.

### Slow buttons (steps 1-5)

Next to each speaker button is a tortoise button. It plays the same recording slowed down, with the pitch unchanged: words at 60 % speed, sentences at 70 %. While it plays:

- **Words:** the headword's letters and its IPA (shown under the headword) light up one sound at a time. "woman" lights up w, o, m, a, n and, underneath, /ˈw/, /ʊ/, /m/, /ə/, /n/.
- **Sentences:** each word lights up while it is read.

How it is made:

- `pron.js` has the IPA for each word, split into sound groups such as `['ou', 'aʊ']` (the letters "ou" spell /aʊ/). The IPA follows what Daniel says when he reads the word alone, so "a" is /eɪ/ and "the" is /ði/.
- The voice server (`tools/tts-lab/lab_server.py`, `/slow_batch`) takes the stored normal clip and slows it down with Rubber Band (through ffmpeg). It then finds when each letter is heard with forced alignment, using `facebook/wav2vec2-large-960h-lv60-self`. It also writes down what a phoneme model (`facebook/wav2vec2-lv-60-espeak-cv-ft`) hears, as `heard`, which was used to check the IPA.
- The tts function's admin action `slow` stores two files next to the normal clip: `slow1/{voice}/{same name}.mp3` and `.json`, the timing file. The page lights each sound from the moment the aligner marks until halfway to the next one. If a slow clip is missing, the page plays the normal clip slowed down by the browser, without highlighting.

To add slow buttons for more steps (for example 6-10):

1. Add the words to `pron.js`. Their letters must spell the word exactly; silent letters join a neighbouring group.
2. Start the pod, then send the output of `python3 tools/slow_items.py 6 10` as the request body, about 22 items per call. Check that each `heard` matches the IPA, then stop the pod.
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
