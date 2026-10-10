# Basic 1000

A step-by-step English course built on 1,000 basic words. Every definition uses only words from earlier steps.

Live site: https://basic-1000.vercel.app

## What's in this folder

| Path | What it is |
|---|---|
| `index.html` | The whole website: layout, lessons, quizzes, review, dictionary and Supabase sign-in |
| `figures.js` | Animated stick-figure scenes (D3), one per word; all of Unit 1 (steps 1-10) so far |
| `data-1.txt` ... `data-4.txt` | The 1,000 words the site loads (250 per file) |
| `content/course.json` | The full course data: steps, definitions, examples |
| `content/check_course.py`, `content/vocab.py` | Checks every course rule. Run after editing `course.json` |
| `tools/build_data.py` | Rebuilds the four data files from `content/course.json` |
| `supabase/migrations/0001_create_progress.sql` | The database table and security rules for saved progress |
| `.vercelignore` | Keeps everything except the website files out of the Vercel deployment |

## Editing the course

1. Edit `content/course.json`.
2. Run `python3 content/check_course.py` and fix anything it reports.
3. Run `python3 tools/build_data.py` to rebuild the data files.
4. Deploy.

## Deploying

From this folder: `npx vercel --prod` (Vercel project `basic-1000`). Only `index.html`, `figures.js` and the data files are uploaded.

## Services

- **Vercel** project `basic-1000`, free Hobby plan (non-commercial use).
- **Supabase** project `basic-1000` (Singapore). The site uses only the public publishable key; the security rules let each signed-in learner read and write only their own progress row.
