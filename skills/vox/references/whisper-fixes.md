# Whisper Post-Processing Reference

Corrections ranked by measured frequency, derived from a 1.8M-word French corpus
(227 transcripts, `large-v3`). Counts are the evidence for the ranking — apply the
top sections first, they carry the volume.

The corpus is single-domain and French, so treat the absolute numbers as
indicative. The phenomena themselves — hallucinations, decoder loops, boundary
duplication, missing punctuation — are properties of the decoder, not of the
subject matter, and show up in any language.

Read [Section 10](#10-do-not-correct-these) before writing any rule. Several
categories that look obvious are **empty** in practice, and acting on them only
introduces regressions.

## Ground rules

- Fix **form**, never **content**. Do not reword, summarize, or repair the
  speaker's grammar — a transcript is a record of what was said.
- Never invent. Mark an unintelligible passage `[inaudible]` rather than guessing.
- Ask the user for a glossary (names, acronyms, jargon) instead of inferring
  domain spellings. Proper nouns are the one category the model reliably fails,
  and the one you cannot derive from context.

## 1. Silence hallucinations — highest priority

On silent stretches Whisper emits subtitling boilerplate. Always delete outright;
never treat as content.

| Artifact | Occurrences |
|---|---|
| `Sous-titrage Société Radio-Canada` | 1766 |
| `Sous-titrage ST' 501` | 296 |
| `Merci.` alone on a segment | 426 |
| `Abonnez-vous`, `Merci d'avoir regardé` | 15 |
| A bare URL repeated across segments | 148 |

English audio produces the same family: `Thanks for watching!`, `Please
subscribe`, `Subtitles by ...`, `Amara.org`, `♪`, `[Music]`, `[Applause]`, and a
closing credit line duplicated at the very end of the file.

Present in **73 of 227 files**. Some files are ~100% artifact (e.g. 84 hits for
252 words) — if the hallucination-to-word ratio approaches 1.0, the recording has
no usable content; report that instead of "cleaning" it.

## 2. Decoder repetition loops

Distinct from boundary duplication (§3). A single token repeats hundreds of times.
Measured: 300 runs of ≥5 identical consecutive tokens, 24,414 junk tokens, 106 files.

**Detection signature: run lengths pin to 221–223** — that's the decoder's internal
limit, not speech. Longest observed run: ×2647.

Loop tokens are ordinary words (`des`, `les`, `tu`, `avec`, `ça`, `pour`) so they
cannot be blacklisted — detect by *run length*, not by vocabulary. Collapse any run
of ≥5 identical consecutive tokens to one.

Phrase-level loops occur too (a 3-4 word n-gram repeated ≥4× consecutively). Apply
the same collapse.

Beware the promoted-proper-noun trap: a looped token gets capitalized and reads as a
name. One corpus token appeared 2462 times, of which only 10 were genuine.

## 3. Segment-boundary duplication

The last word of segment N repeats as the first word of segment N+1: **4267
occurrences over 330,352 boundaries (1.29%)**, plus 1402 three-word overlaps.

Top offenders are short, high-frequency words (`merci` 391, `ça` 230, `ok` 229,
`là` 165, `c'est` 130).

```
seg N   : "...ça va être le premier cours sur la fiscalité"
seg N+1 : "fiscalité du contribuable"
```

**This leaks into the `text` field**, which is the concatenation. Any reconstruction
from `segments` must dedupe boundaries.

The mirror case: a word split across two blocks appears truncated in one and
duplicated in the other. Merge it into the block where the word begins.

## 4. Punctuation — bimodal, not uniform

Corpus median is a healthy 22 words per period, but the distribution is bimodal:

| Condition | Files (of 227) |
|---|---|
| Zero periods in the entire file | 23 |
| Zero question marks | 43 |
| Zero commas | 19 |
| More than 100 words per period | 55 |

Worst observed: 17,087 words with **0 periods**; another with 11,500 words and zero
periods, commas and question marks.

**So: measure before rewriting.** If the file is under ~30 words per period, leave
punctuation alone. If it is over 100, the decoder emitted none and full
re-punctuation is warranted.

Question marks are structurally under-generated: 9313 interrogative markers
(`est-ce que`, `qu'est-ce`, `pourquoi`, `comment`, `combien`, `c'est quoi`) for 5526
`?` — and 43 files have none at all. `;` and `:` never appear in the entire corpus.

Only 21.4% of segments end in `.`, `!` or `?`. Mean segment length is 5.5 words, so
segment boundaries are **not** sentence boundaries — never punctuate by segment.

Languages with paired marks need the opening `¿` and `¡`, which Whisper almost
never emits.

## 5. Capitalization

16 files are entirely lowercase (<0.1% uppercase, corpus median 1.55%); 43 sit under
0.5%. **12 of those 16 also have zero periods** — the two defects are correlated and
signal the same degraded decode. Check both together, and restore both together.

## 6. Diacritics

Restore from grammatical context, never by blind search-and-replace. In French the
measured gain is small (§10) — other languages lose accents far more often.

**Spanish**: `como`/`cómo` (question), `esta`/`está` (verb), `mas`/`más` (quantity),
`si`/`sí` (yes), `el`/`él` (pronoun), `que`/`qué` (question), `tambien`/`también`,
`informacion`/`información`.

**Portuguese**: `nao`/`não`, `voce`/`você`, `esta`/`está`, `sao`/`são`, `ja`/`já`.

**German**: umlauts and `ß` may come back as `ae/oe/ue/ss`.

## 7. Hyphenation and compounds

Both spellings coexist at scale — this is normalization, not transcription error.

| Preferred | Variant to fix | Counts |
|---|---|---|
| `c'est-à-dire` | `c'est à dire` | 675 / 769 |
| `est-ce que` | `est ce que` | 1976 / 754 |
| `qu'est-ce` | `qu'est ce` | 761 / 252 |
| `celui-là` | `celui là` | 710 / 267 |
| `celle-là` | `celle là` | 204 / 169 |
| `au-dessus` | `au dessus` | 172 / 193 |
| `là-haut` | `là haut` | 230 / 80 |
| `micro-entreprise` | `micro entreprise` | 27 / 10 |
| `auto-entrepreneur` | `auto entrepreneur` | 4 / 2 |

`peut-être` (1825) vs `peut être` (484): hyphenate only the adverb. `peut être` is
correct when it's the verb (`ça peut être utile`).

Multi-word brand names follow the same pattern — the model splits or joins them
inconsistently. That is a glossary matter, not a rule.

## 8. Number and time formatting — inconsistent, not wrong

Pick one style per document; the corpus mixes all of them.

- Thousands: spaced `15 000` (1926) vs glued `26400` (3339)
- Shorthand: `25k`, `50k` (909)
- Decimals use the French comma: `80,25` (1684) — English uses a point, and the
  model follows the detected language, not the speaker
- Times: `15h30` (934), `15h` (605), `15 heures` (370) — `15:30` never appears
- Percent: `15%` (1564) vs `15 pour cent` (3)
- Currency: `dollars` (814) vs `$` (346); `euros` (372) vs `€` (23)
- Locale spacing: French puts a space before `%`, `€`, `:`, `?`, `!`
- Slang currency terms (`balles`, `bucks`, `quid`) are register, not error — keep

## 9. Language detection

Whisper detects the language from the first ~30 seconds. Consequences:

- Audio that opens with music, an intro jingle, or a foreign greeting can be
  detected wrong, and the whole file is then transcribed — or translated — into
  that language. Re-run with `-l <code>`; no post-processing fixes it.
- Code-switching mid-file is transcribed in the detected language, sometimes
  phonetically.

## 10. Do NOT correct these

Each was tested against the corpus and found empty or already correct. Writing rules
for them costs tokens and causes regressions.

**Phonetized anglicisms — essentially nonexistent.** `large-v3` spells recognized
English terms correctly, including technical vocabulary borrowed into French.
Tested and absent: phonetic manglings of common loanwords. Only *proper nouns*
fail — brands, products, people, platforms.

**Disfluencies — already stripped.** `euh` appears 296 times in 1.8M words (1 per
6145). Nothing to remove. Strip fillers only if the user explicitly asks; they are
part of the record.

**Spelled-out numbers — absent.** `mille` 142, `vingt` 7, `trente` 2;
"quinze heures" and "dix pour cent" appear **zero** times.

**Given names — already stable.** No phonetic variants found across 40+ names. Only
accent/spelling normalization applies: `Erwan`/`Erwann`, `Loïc`/`Loic`,
`Etienne`/`Étienne`.

**Terms that never occur in your corpus** — verify before writing any rule. Half of
a plausible-looking rule list typically has zero matches.

### French homophones — deliberately minimal

**Whisper handles French homophones well.** Generic patterns yield >90% false
positives (`tout à fait`, `qui ont fait`, `s'est bien passée` are all correct). Total
realistic gain is ~120 corrections across 1.8M words. Do not build aggressive rules.

Only closed, unambiguous strings are safe — `a` → `à` in: `a partir de` (14),
`a l'inverse` (13), `a peu près` (11), `a chaque fois` (11), `a la baisse` (6),
`a l'achat` (4), `a nouveau`, `a la hausse`, `a gauche`. **62 total.**

Context-dependent, verify each before changing: `ce`→`se` before a pronominal verb
(11), `ou`→`où` in locatives (~24, many false positives), `sa`→`ça` (5), `ça`→`sa`
(2), `la haut`→`là-haut` (3).

Tested with **zero** detectable errors — skip entirely: `sont`→`son`, `ces`→`ses`,
`peut`→`peu`, `sur`→`sûr`. (`du`→`dû`: 2 occurrences, not worth a rule.)

English and Spanish were not measured here; the same discipline applies — verify
frequency on your own output before writing a rule.

## 11. Speaker attribution

Whisper does not do diarization: it produces one undifferentiated stream. Insert
`[Name]:` markers only when speakers are clearly identifiable from context, and
never guess who is talking. Real speaker separation requires a diarization tool.

## 12. SRT editing rules

When editing `.srt` output:

1. Never modify timestamp lines (those containing `-->`)
2. Never modify sequence numbers
3. Edit only the text between timestamps
4. Keep the block count identical
5. Preserve blank lines between blocks

Corpus note: the `words` field is `null` on all 227 files — no word-level timestamps
are available unless `--words` was passed at transcription time.
