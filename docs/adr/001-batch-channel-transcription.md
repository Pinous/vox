# ADR-001 : Batch transcription de chaîne YouTube + upload Google Drive

**Date** : 2026-04-01
**Statut** : Accepté

## Contexte

On utilise `vox` pour transcrire des vidéos YouTube une par une. Le besoin est apparu de transcrire en masse les vidéos d'une chaîne — en l'occurrence les vidéos "scalping nasdaq" de @XEILOSTRADING, filtrées sur 2025-2026 — puis de pousser les transcripts sur Google Drive sans garder les fichiers audio en local (espace disque limité).

Aucune fonctionnalité batch n'existait. Le CLI ne gérait qu'une seule URL ou fichier à la fois.

Second besoin : organiser les transcripts comme une knowledge base exploitable par Claude Code. Chaque vidéo a un `meta.md` (auteur, topics, résumé LLM), et un `index.md` centralise tous les metas pour permettre une recherche rapide sans lire chaque transcript.

## Décisions

### Nouvelle commande `vox channel`

On a créé une commande dédiée plutôt qu'un flag `--batch` sur `transcribe`. Raison : le flow est fondamentalement différent (listing → filtrage → boucle → summarize → upload → cleanup). Mélanger ça dans `transcribe` aurait violé SRP.

### rclone comme adaptateur d'upload (pas l'API Google directement)

Trois options étaient sur la table :
1. **OAuth2 + google-api-python-client** — standard mais setup lourd (projet Google Cloud, client_secret.json, flow OAuth interactif)
2. **rclone** — déjà un outil que beaucoup ont configuré, gère le multi-compte Google nativement, zéro dépendance Python supplémentaire
3. **Service Account** — pas de flow interactif mais nécessite un partage de dossier explicite

On a choisi rclone parce que :
- Pas de nouvelle dépendance Python (subprocess comme yt-dlp et ffmpeg)
- Le `u/4` dans l'URL Drive (4ème compte Google) est géré naturellement par rclone
- Pattern cohérent avec le reste du projet : les outils externes sont appelés en subprocess via des adapters

Le port `FileUploader` est volontairement générique (pas couplé à rclone). Demain on peut brancher S3, Dropbox, ou l'API Google directe sans toucher au use case.

### Organisation des fichiers : knowledge base structure

Structure locale :
```
~/transcripts/
├── CLAUDE.md                              ← contexte pour Claude Code
├── index.md                               ← concaténation de tous les meta.md
├── 2025-03-15_scalping-nasdaq-session-1/
│   ├── transcript.txt
│   ├── transcript.srt
│   ├── transcript.json
│   └── meta.md
└── 2025-04-20_scalping-nasdaq-session-2/
    ├── transcript.txt
    └── meta.md
```

Structure sur le remote (même hiérarchie avec chaîne en plus) :
`gdrive:Transcripts/XEILOSTRADING/Scalping Nasdaq Session 1/`

Pourquoi cette structure :
- **Dossier par vidéo avec date-slug** : triable chronologiquement, lisible par un humain
- **meta.md** : métadonnées structurées (auteur, topics, résumé) pour recherche rapide
- **index.md** : le "hack" — Claude Code lit ce seul fichier et connaît tous les transcripts
- **CLAUDE.md** : explique la structure à Claude Code automatiquement

### Résumé et topics via Claude CLI (par défaut)

Par défaut, `vox channel` utilise le CLI `claude` en subprocess pour générer le résumé et les topics. C'est l'abonnement Claude de l'utilisateur qui est utilisé — pas besoin d'API key, pas de dépendance Python supplémentaire.

Le summarizer est pluggable via le flag `--summarizer` :

| Valeur | Adapter | Quand l'utiliser |
|--------|---------|------------------|
| `auto` (défaut) | `ClaudeSummarizer` si `claude` dans PATH, sinon `NoopSummarizer` | Usage normal — marche out-of-the-box si Claude Code est installé |
| `claude` | `ClaudeSummarizer` | Forcer le CLI Claude |
| `anthropic` | `AnthropicSummarizer` | API directe, nécessite `ANTHROPIC_API_KEY` + `pip install anthropic` |
| `none` | `NoopSummarizer` | Skip le résumé/topics |

Pourquoi ce design :
- **Par défaut ça marche** : si tu as Claude Code, tu as `claude` dans ton PATH, donc summary + topics sont générés sans config
- **Pluggable** : le port `TranscriptSummarizer` est un Protocol Python. Pour ajouter un backend (OpenAI, Mistral, etc.), il suffit de créer un adapter avec `summarize(text, title) -> SummaryResult` et de l'ajouter dans `_build_summarizer()`
- **Pas de dépendance forcée** : le SDK Anthropic est un import lazy dans l'adapter, pas une dépendance du projet

### Traitement séquentiel (pas parallèle)

Une vidéo à la fois : download → clean → transcribe → summarize → meta → upload → cleanup → suivante. Raisons :
- Contrôle de l'espace disque (avec `--cleanup`, on ne stocke qu'une vidéo à la fois)
- MLX Whisper utilise le GPU — paralléliser n'apporterait rien
- Simplifie le debug et le suivi de progression

### Tolérance aux erreurs partielles

Si une vidéo échoue (réseau, format non supporté, etc.), on enregistre l'erreur et on continue. Le `BatchResult` final donne le bilan `succeeded/failed`. Le meta.md n'est pas écrit pour les vidéos en échec. L'index.md ne contient que les vidéos réussies.

## Architecture

```
Models (couche interne)
  ChannelVideo (+duration_seconds), DateRange, BatchResult
  SummaryResult, VideoMetadata
  + exceptions : ChannelListingError, UploadError

Ports (interfaces)
  ChannelLister, FileUploader, FileCleaner
  TranscriptSummarizer, MetadataWriter

Use Case
  BatchTranscribeUseCase
    ├── compose TranscribeUseCase (pas de duplication)
    ├── appelle TranscriptSummarizer pour enrichir
    └── appelle MetadataWriter pour meta/index/CLAUDE.md

Adapters (couche externe)
  YtdlpChannelLister, RcloneUploader, DiskFileCleaner
  ClaudeSummarizer / AnthropicSummarizer / NoopSummarizer
  DiskMetadataWriter
  CLI : channel_cmd.py (--summarizer auto|claude|anthropic|none)
```

## Fichiers créés

| Fichier | Rôle |
|---------|------|
| `src/vox/models/channel_video.py` | Video YouTube (id, titre, date, chaîne, durée) |
| `src/vox/models/date_range.py` | Filtre par années (factory `from_years`) |
| `src/vox/models/batch_result.py` | Résultat batch (succès/échecs par vidéo) |
| `src/vox/models/summary_result.py` | Résultat LLM (summary + topics) |
| `src/vox/models/video_metadata.py` | Contenu du meta.md |
| `src/vox/ports/channel_lister.py` | Protocol : lister les vidéos d'une chaîne |
| `src/vox/ports/file_uploader.py` | Protocol : uploader un fichier (générique) |
| `src/vox/ports/file_cleaner.py` | Protocol : supprimer un fichier |
| `src/vox/ports/transcript_summarizer.py` | Protocol : résumer un transcript |
| `src/vox/ports/metadata_writer.py` | Protocol : écrire meta/index/CLAUDE.md |
| `src/vox/adapters/ytdlp_channel_lister.py` | yt-dlp --flat-playlist --dump-json |
| `src/vox/adapters/rclone_uploader.py` | rclone copy vers remote |
| `src/vox/adapters/disk_file_cleaner.py` | path.unlink() |
| `src/vox/adapters/claude_summarizer.py` | Claude Sonnet via CLI `claude -p` (abonnement) |
| `src/vox/adapters/anthropic_summarizer.py` | Claude Sonnet via SDK Anthropic (API key) |
| `src/vox/adapters/noop_summarizer.py` | No-op quand on skip le résumé |
| `src/vox/adapters/disk_metadata_writer.py` | Écrit meta.md, index.md, CLAUDE.md |
| `src/vox/adapters/cli/channel_cmd.py` | Commande Click `vox channel` |
| `src/vox/use_cases/batch_transcribe.py` | Orchestration batch |

## Fichiers modifiés

| Fichier | Changement |
|---------|------------|
| `src/vox/models/exceptions.py` | +`ChannelListingError`, +`UploadError` |
| `src/vox/adapters/cli/app.py` | +`main.add_command(channel)` |
| `src/vox/use_cases/transcribe.py` | +`output_stem` sur `TranscribeRequest` |

## Conséquences

- `vox channel` produit une knowledge base prête à l'emploi pour Claude Code
- Par défaut, summary + topics sont générés via l'abonnement Claude (CLI `claude -p`)
- Le `CLAUDE.md` + `index.md` permettent à Claude de naviguer les transcripts sans tout lire
- Le flag `--summarizer` rend le backend LLM pluggable (claude, anthropic, none, et extensible)
- Le port `FileUploader` peut être réutilisé pour d'autres backends de stockage
- Le `ChannelLister` peut être étendu pour d'autres sources (playlists, hashtags, etc.)
- Les tests unitaires couvrent le use case via des fakes (108 tests, pas de réseau, pas de GPU)
