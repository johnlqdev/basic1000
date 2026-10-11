# Basic 1000

A step-by-step English course built on 1,000 basic words. Every definition uses only words from earlier steps.

Live site: https://basic-1000.vercel.app

## What's in this folder

| Path | What it is |
|---|---|
| `index.html` | The whole website: layout, lessons, quizzes, review, dictionary and Supabase sign-in |
| `figures.js` | Animated stick-figure scenes (D3), one per word; all of Unit 1 (steps 1-10) so far |
| `audio.js` | Speaker buttons: plays each word and example in a woman's or man's voice |
| `data-1.txt` ... `data-4.txt` | The 1,000 words the site loads (250 per file) |
| `content/course.json` | The full course data: steps, definitions, examples |
| `content/check_course.py`, `content/vocab.py` | Checks every course rule. Run after editing `course.json` |
| `tools/build_data.py` | Rebuilds the four data files from `content/course.json` |
| `supabase/migrations/` | Database table and security rules for saved progress; the public `audio` bucket |
| `supabase/functions/tts/index.ts` | Text-to-speech function: text + voice in, MP3 address out |
| `tools/audio_items.py` | Lists the clips a range of steps needs, as a request for the tts function |
| `.vercelignore` | Keeps everything except the website files out of the Vercel deployment |

## Editing the course

1. Edit `content/course.json`.
2. Run `python3 content/check_course.py` and fix anything it reports.
3. Run `python3 tools/build_data.py` to rebuild the data files.
4. Deploy.

## Deploying

From this folder: `npx vercel --prod` (Vercel project `basic-1000`). Only `index.html`, `figures.js`, `audio.js` and the data files are uploaded. Pushing to `main` on GitHub (`johnlqdev/basic1000`) also deploys.

## Services

- **Vercel** project `basic-1000`, free Hobby plan (non-commercial use).
- **Supabase** project `basic-1000` (Singapore). The site uses only the public publishable key; the security rules let each signed-in learner read and write only their own progress row.

## Audio

Voices come from **Kokoro-82M** (open source, Apache-2.0), run with the Kokoro-FastAPI server on a RunPod CPU pod named `basic1000-tts` (about $0.12 an hour, only while it is running). Woman: `af_heart`. Man: `am_michael`. Speed 0.92.

- Every clip is made once and kept in the public Supabase bucket `audio`, at `{voice}/{first 32 hex of sha256(voice + "|" + text)}.mp3`. The site works out that address itself, so stored clips play with no server call.
- Ask for any text: `GET https://duptugctgzemfczbtvgj.supabase.co/functions/v1/tts?text=I%20am%20a%20woman.&voice=woman` returns `{ "url": ... }`. A new text is made only while the pod is running; otherwise the reply is 503 and the site falls back to the browser's own voice.
- Admin actions need the `x-admin-token` header (the token is in the Supabase vault as `tts_admin_token`): `status`, `start`, `stop`, `batch`, `pods`, `create`, `delete`.
- To add clips for new steps: start the pod, send `python3 tools/audio_items.py 11 20` as a `batch` (about 15 items per call), then stop the pod.
- To change a voice, edit `VOICES` in both `supabase/functions/tts/index.ts` and `audio.js`, redeploy both, and make the clips again.
- The function reads the RunPod key from the Supabase secret `RUNPOD_API_KEY`.
