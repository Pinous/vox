# Common Whisper Transcription Mistakes

Reference for post-processing a raw transcript. Domain-agnostic: it covers the
errors Whisper makes on any audio, in any field.

## Ground rules

- Fix **form**, never **content**. Do not reword, summarize, or repair the
  speaker's grammar — a transcript is a record of what was said.
- Keep SRT structure intact: same number of blocks, same timestamps. Edit the
  text inside a block, never the timing line.
- Never invent. If a passage is unintelligible, mark it `[inaudible]` rather
  than guessing.
- Ask the user for a glossary (names, acronyms, jargon) instead of guessing
  domain-specific spellings.

## Hallucinations on silence and music

The single most common Whisper failure. On silence, music, or background noise
it emits training-set boilerplate that was never spoken. Delete these blocks —
do not try to "correct" them.

Typical artifacts:

- `Sous-titres réalisés par la communauté d'Amara.org`
- `Merci d'avoir regardé cette vidéo`, `Abonnez-vous !`
- `Thanks for watching!`, `Please subscribe`, `Subtitles by ...`
- `Amara.org`, `♪`, `[Music]`, `[Applause]`
- A closing credit line duplicated at the very end of the file

Suspicion signals: the block sits over a long timestamp gap, its wording is
unrelated to everything around it, or it appears verbatim at both start and end.

## Repetition loops

Whisper can lock onto a phrase and repeat it across consecutive blocks, usually
over silence or noise. Keep the first occurrence, drop the loop. Check the
timestamps: a loop often spans an implausibly long stretch for that little text.

## Punctuation and capitalization

- Restore sentence boundaries. Whisper produces run-on sentences; split where
  the topic changes, the speaker changes, or the SRT shows a pause > 1.5 s.
- Capitalize sentence starts and proper nouns.
- Languages with paired marks: Spanish needs the opening `¿` and `¡`, which
  Whisper almost never emits.
- Quotation marks and apostrophes are often ASCII; normalize to the language's
  convention if the user cares about typography.

## Diacritics

Whisper drops accents, especially on short function words. Restore from
grammatical context, never blindly search-and-replace.

**French** — the frequent pairs:
`a`/`à`, `ou`/`où`, `sur`/`sûr`, `du`/`dû`, `la`/`là`, `des`/`dès`,
`ete`/`été`, `deja`/`déjà`, `tres`/`très`, `apres`/`après`.

**Spanish**:
`como`/`cómo` (question), `esta`/`está` (verb), `mas`/`más` (quantity),
`si`/`sí` (yes), `el`/`él` (pronoun), `que`/`qué` (question),
`tambien`/`también`, `informacion`/`información`.

**Portuguese**:
`nao`/`não`, `voce`/`você`, `esta`/`está`, `sao`/`são`, `ja`/`já`.

**German**: umlauts and `ß` may come back as `ae/oe/ue/ss` — restore them.

## Homophones

Only context disambiguates these; Whisper picks the most frequent form.

**French**: `et`/`est`, `on`/`ont`, `son`/`sont`, `ce`/`se`, `ces`/`ses`/`c'est`/`s'est`,
`peu`/`peut`, `quand`/`quant`, `leur`/`leurs`, `tout`/`tous`.

**English**: `their`/`there`/`they're`, `its`/`it's`, `your`/`you're`,
`to`/`too`/`two`, `then`/`than`, `affect`/`effect`.

**Spanish**: `haber`/`a ver`, `hay`/`ahí`/`ay`, `porque`/`por qué`.

## Numbers, units, dates

Whisper is inconsistent — sometimes digits, sometimes words, within the same
file. Pick one convention and apply it throughout:

- Spelled-out numbers that should be digits: percentages, prices, measurements,
  version numbers, years.
- Units glued to the number (`10km` → `10 km`), and locale spacing (French puts
  a space before `%`, `€`, `:`, `?`, `!`).
- Decimal separator: `,` in French/Spanish/German, `.` in English. Whisper
  mixes them.
- Spoken dates and times ("le premier mars", "half past three") — normalize only
  if the user asked for it.

## Proper nouns, acronyms, borrowed words

- Acronyms come out spaced or lowercased (`s a s`, `sas` → `SAS`).
- Person, place, and product names are the most error-prone tokens in any
  transcript. Prefer the user's glossary; otherwise flag rather than invent.
- Borrowed English words inside another language are often transcribed
  phonetically — restore the standard spelling.

## Segment boundaries

- A word cut across two blocks appears truncated in one and duplicated in the
  other. Merge it into the block where the word begins.
- Stutters and exact duplicates at a boundary (`the the`, `je je`) are usually
  segmentation artifacts, not speech.
- A block with text but a near-zero duration is suspect.

## Language detection

Whisper detects the language from the first ~30 seconds. Consequences:

- Audio that opens with music, an intro jingle, or a foreign greeting can be
  detected wrong, and the whole file is then transcribed — or translated —
  into that language. Re-run with `-l <code>`.
- Code-switching mid-file is transcribed in the detected language, sometimes
  phonetically. There is no fix in post-processing; re-run on the relevant
  section.

## Filler words

`um`, `uh`, `euh`, `este`, `o sea`, `like`, `you know`, `voilà`, `en fait`.
Remove them **only if the user asks** — they are part of the record, and
stripping them silently changes the transcript's fidelity.

## Speaker attribution

Whisper does not do diarization: it produces one undifferentiated stream. If
speakers are identifiable from context, prefix blocks with `[Name]:`, but never
guess who is talking. For real speaker separation, a diarization tool is
required.
