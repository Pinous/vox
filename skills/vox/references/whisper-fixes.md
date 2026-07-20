# Whisper Post-Processing Reference

Corrections ranked by measured frequency, derived from a 1.8M-word French corpus
(227 transcripts, `large-v3`, trading/finance domain). Counts are the evidence for
the ranking — apply the top sections first, they carry the volume.

Read [Section 9](#9-do-not-correct-these) before writing any rule. Several
categories that look obvious are **empty** in practice, and acting on them only
introduces regressions.

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

Present in **73 of 227 files**. Some files are ~100% artifact (e.g. 84 hits for
252 words) — if the hallucination-to-word ratio approaches 1.0, the recording has
no usable content; report that instead of "cleaning" it.

## 2. Decoder repetition loops

Distinct from boundary duplication (§7). A single token repeats hundreds of times.
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

## 3. Domain vocabulary — certain corrections

### propfirm — the single highest-volume error

**1042 wrong vs 12 correct.** The term is essentially never transcribed right.

| Wrong | Occurrences |
|---|---|
| `propre firme` / `propres firmes` | 447 |
| `profs firme` / `profs firm` | 255 |
| `propes firme` / `propes firmes` | 209 |
| `profirme` / `profirm` | 59 |
| `profilme` / `profilmes` | 28 |
| `prop firm` / `prop firme` (spaced) | 22 |
| `profilère(s)` / `profilière(s)` | 9 |
| `multiprop firme`, `multipro firme` | 15 |
| Long tail: `profilien`, `profilaires`, `profilums`, `profilité`, `propure firme`, `croque firme`, `propre ferme` | ~30 |

All → `propfirm` / `propfirms` / `multipropfirm`. Note `propes` standing alone also
means propfirms.

### Instruments

| Wrong | Correct | Occurrences |
|---|---|---|
| `Eurostox` | `Eurostoxx` | 221 |
| `Euro Stock` / `euro stocks` | `Eurostoxx` | 142 |
| `Eurostock` | `Eurostoxx` | 18 |
| `Bound` | `Bund` | 205 |
| `tiques` | `ticks` | 8 |
| `renge` | `range` | 2 |

`Bound` → `Bund` only in an instrument context. Plain `bond` (62 occ.) is the
legitimate French noun for a bounce — leave it.

### `carnet d'ordre` drift

62 phonetic variants: `carnet d'or` (30), `carnet d'accord` (16), `carnet d'ordes`
(5), `carnet d'eau` (4), `carnet d'orne` (3), `carnet d'arbre(s)` (3),
`carnet d'orgue` (1). All → `carnet d'ordre(s)`.

### Brands and platforms

| Wrong | Correct | Occurrences |
|---|---|---|
| `Lucide` | `Lucid` | 167 |
| `Xellos` / `Zelos` / `Zellos` / `Xelo` | `Xelos` | 163 |
| `Bullnox` / `Boodlox` | `Bulenox` | 75 |
| `discorde` | `Discord` | 43 |
| `Tradify` / `Tradesy` | `Tradeify` | 25 |
| `click size` / `clic size` / `clipsize` | `clip size` | 23 |
| `rythmique` / `Rhythmic` | `Rithmic` | 23 |
| `Funden Next` / `Fundenext` | `FundedNext` | 6 |
| `edging` | `hedging` | 5 |
| `Tradervate` | `Tradovate` | 4 |
| `Cantover` / `Quantover` | `Quantower` | 3 |
| `Motivwave` | `MotiveWave` | 1 |
| `bidet ask` | `bid et ask` | 1 |
| `URSAF` | `URSSAF` | 7 |

`rythmique` is only wrong when naming the data feed — the French adjective is
legitimate elsewhere. Same caution for `discorde`.

**Already correct, never touch:** Nasdaq, Russell, DAX, Apex, TPT, Tradovate,
TradingView, MetaTrader, FTMO, MyFundedFuture, ATAS, CME, Eurex, Bollinger,
Fibonacci, VWAP, FOMC, NFP, CPI, PMI, AMF — zero faulty variants observed.

## 4. Segment-boundary duplication

The last word of segment N repeats as the first word of segment N+1: **4267
occurrences over 330,352 boundaries (1.29%)**, plus 1402 three-word overlaps.

Top offenders: `merci` 391, `ça` 230, `ok` 229, `là` 165, `c'est` 130.

```
seg N   : "...ça va être le premier cours sur la fiscalité"
seg N+1 : "fiscalité du trader propfirm"
```

**This leaks into the `text` field**, which is the concatenation. Any reconstruction
from `segments` must dedupe boundaries.

## 5. Punctuation — bimodal, not uniform

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

## 6. Capitalization

16 files are entirely lowercase (<0.1% uppercase, corpus median 1.55%); 43 sit under
0.5%. **12 of those 16 also have zero periods** — the two defects are correlated and
signal the same degraded decode. Check both together, and restore both together.

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
| `Topstep` | `Top Step` | 29 / 363 |
| `TradingView` | `Trading View` | 53 / 40 |
| `micro-entreprise` | `micro entreprise` | 27 / 10 |
| `auto-entrepreneur` | `auto entrepreneur` | 4 / 2 |

`peut-être` (1825) vs `peut être` (484): hyphenate only the adverb. `peut être` is
correct when it's the verb (`ça peut être utile`).

## 8. Number and time formatting — inconsistent, not wrong

Pick one style per document; the corpus mixes all of them.

- Thousands: spaced `15 000` (1926) vs glued `26400` (3339)
- Shorthand: `25k`, `50k` (909)
- Decimals use the French comma: `80,25` (1684)
- Times: `15h30` (934), `15h` (605), `15 heures` (370) — `15:30` never appears
- Percent: `15%` (1564) vs `15 pour cent` (3)
- Currency: `dollars` (814) vs `$` (346); `euros` (372) vs `€` (23)
- `balles` (846) is slang for euros — keep it, it's register, not error

## 9. Do NOT correct these

Each was tested against the corpus and found empty or already correct. Writing rules
for them costs tokens and causes regressions.

**Phonetized anglicisms — essentially nonexistent.** `large-v3` spells recognized
English terms correctly: `scalping` 844, `drawdown` 291, `stop loss` 305,
`payout` 629, `challenge` 1550, `clip size` 560, `money management` 131. Tested and
absent: `skalping`, `nasdak`, `bolinger`, `drawdawn`, `poolback`, `brekout`,
`stoploss`, `taïm frame`. Only *brand names* (§3) fail.

**Disfluencies — already stripped.** `euh` appears 296 times in 1.8M words (1 per
6145). Nothing to remove.

**Spelled-out numbers — absent.** `mille` 142, `vingt` 7, `trente` 2;
"quinze heures" and "dix pour cent" appear **zero** times.

**Terms with zero occurrences** — do not add rules: `backtest`, `breakout`,
`win rate`, `PFU`, `prélèvement forfaitaire`, `MT4`/`MT5`, `MACD`, `Jigsaw`.

**ICT/SMC lexicon — absent.** `OTE` 0, `killzone` 0, `BOS` 0, `CHOCH` 0,
`smart money` 0, `London session` 0. This domain uses proprietary vocabulary
instead (§10).

**Given names — already stable.** No phonetic variants found across 40+ names. Only
accent/spelling normalization applies: `Erwan`/`Erwann`, `Loïc`/`Loic`,
`Etienne`/`Étienne`.

**Tax vocabulary — correct.** `BNC`, `micro-entreprise`, `flat tax`, `TVA`, `SASU`
all transcribe cleanly.

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

## 10. Proprietary terms — protect from "correction"

House vocabulary a naive corrector would rewrite. These are correct as-is:

`matelas` (4593), `amplitude` (3233), `dynamique` (3114), `carnet` (3441),
`retracement` (1168), `bougie` (1106), `vol` = volatilité (1097), `mèche` (511),
`liquidité` (304), `craquage`, `carnet lourd` / `carnet léger`, `zone de pierre`,
`branche de l'arbre`, `clip size`, `payout`, `PA` = compte financé, `TPT Pro`.

`Michigan` (58) is legitimate — the consumer confidence index, not a loop artifact.

## 11. SRT editing rules

When editing `.srt` output:

1. Never modify timestamp lines (those containing `-->`)
2. Never modify sequence numbers
3. Edit only the text between timestamps
4. Keep the block count identical
5. Preserve blank lines between blocks

Corpus note: the `words` field is `null` on all 227 files — no word-level timestamps
are available unless `--words` was passed at transcription time.
