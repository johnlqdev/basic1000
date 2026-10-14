# Basic 1000 – bootstrap course data

The Basic 1000 word list, ordered into **200 steps of 5 words**. Each definition uses only words
from earlier steps. No UI and no media: this package is the data layer, plus a checker that
enforces the rules.

## Files

| File | What it is |
|---|---|
| `course.json` | The full course: steps, and every word with its definition, examples and dependencies. This is the source of truth. |
| `course_words.csv` | The same 1,000 words flattened to one row each, for review in a spreadsheet. |
| `check_course.py` | Validates `course.json` against every rule below. Run it after any edit. |
| `vocab.py` | The word-matching rules used by the checker (endings, irregular forms, free compounds). |

```
python3 check_course.py            # prints OK, or lists every broken rule and exits with code 1
```

## How the bootstrap works

1. **Starter block (steps 1–6).** There are 30 words: *I, am, a, man, woman, you, are, he, she, is…*. *am*, *is* and *are* are their own words here, and *be* (with *was, were, been, being*) comes at step 11. Their
   examples use only starter words, for example "I am a man.", "The cat is small." and "What is this?".
2. **Seed words (400).** These are taught without a text definition:
   - `picture` (191): things you can show, such as *apple, dog, red, rain*.
   - `action` (92): movements and directions, such as *run, push, up, between*.
   - `demo` (117): grammar and function words, plus a few very basic ideas (*the, if, would, idea,
     life*), learned through their example sentences.

   The seeds are the course's grounding set. Every definition cycle in the list (*live ↔ life*,
   *question ↔ ask*, *left ↔ right*…) was broken by making one word a seed, or by rewriting a
   definition. The definition graph is now acyclic.
3. **Defined words (600).** Each is explained in Basic English. The first comes at step 27, and
   the share of defined words grows from about a third of each step (steps 27–60) to about 85%
   (steps 129–200).

### Rules (all enforced by `check_course.py`)

- Every word of the 1,000 appears exactly once, and every step has 5 words.
- A **definition** uses only words from **earlier** steps and never the word itself.
- Every word has at least one **teaching example** that uses only words from earlier steps or the
  same step.
- The **first example** uses the word in its plain form, exactly as listed ("I make a cake.", never
  "I made a cake."; "A cow gives milk.", never "Cows give milk."), and is usable at the word's step.
- Other examples are **review examples**. `available_from_step` says when every word in them is
  known, so they can be scheduled into later reviews.
- Every word in a definition or example must map to one of the 1,000 under these rules:
  - Endings: *-s/-es, -ed, -ing, -er* (doer or comparison), *-est, -ly*, and the prefix *un-*.
  - Irregular forms: *went → go*, *children → child*.
  - Grouped forms: *me/my → I*, *more/most → much*, *better/best → good*.
  - Free compounds from a fixed list: *someone, something, cannot, inside, birthday…*
  - Digits and any other words are rejected.

## Data shape

`course.json`:

```json
{
  "meta":  { "step_size": 5, "teach_modes": {...}, "rules": [...] },
  "steps": [ { "step": 1, "type": "vocabulary", "phase": "starter",
               "words": ["I","you","be","a","man"], "defined_words": 0 }, ... ],
  "words": [ {
      "id": 151, "word": "life", "us_spelling": "", "pos": "noun",
      "step": 31, "teach_mode": "demo",
      "definition": null, "definition_uses": [],
      "examples": [
        { "text": "There is no life on the moon.", "uses": ["there","be","no","life","on","the","moon"],
          "available_from_step": 31, "role": "teach" },
        { "text": "She had a long and happy life.", "uses": [...],
          "available_from_step": 85, "role": "review" } ],
      "grouped_forms": [], "source": "NGSL only", "ngsl_rank": 111 } ]
}
```

`uses` lists headwords, so your app can link each word in a sentence to its entry. `step.type` is
always `"vocabulary"` for now. Grammar steps can be inserted later with their own `type`.

## How the order was chosen

Within the rules, steps are filled greedily, by NGSL frequency and by how many later words each
word helps to explain. When a word's teaching example needs a word not yet learned, the two are
placed in the same step if they fit.

## Known limits

- **One main sense per word.** A few entries give a second sense after "also,". Other senses of
  common words, such as *light* as "not heavy" or *fly* as the insect, are not covered.
- **No grammar steps yet.** Definitions use simple present and past forms and "who/that" clauses.
  These should be taught as grammar steps early, around steps 10–40.
- **The text is hand-written.** It passed the vocabulary checks, but it should be read by a native
  speaker or teacher before launch.
- **Spelling is British.** US spellings are in `us_spelling` and are accepted by the checker.
