from vox.models.clustering import cluster_embeddings
from vox.models.silhouette import silhouette_score
from vox.models.voice_matching import Embedding, cosine_similarity

DEFAULT_MAX_SPEAKERS = 10
SAME_VOICE_SIMILARITY = 0.85


def estimate_speaker_count(
    embeddings: list[Embedding],
    max_speakers: int = DEFAULT_MAX_SPEAKERS,
) -> int:
    if len(embeddings) < 2:
        return 1
    if _all_one_voice(embeddings):
        return 1
    return _best_scoring_count(embeddings, max_speakers)


def _best_scoring_count(
    embeddings: list[Embedding],
    max_speakers: int,
) -> int:
    ceiling = min(max_speakers, len(embeddings))
    scored = [
        (silhouette_score(embeddings, cluster_embeddings(embeddings, n)), n)
        for n in range(2, ceiling + 1)
    ]
    if not scored:
        return 1
    return max(scored)[1]


def _all_one_voice(embeddings: list[Embedding]) -> bool:
    return all(
        cosine_similarity(embeddings[i], embeddings[j]) >= SAME_VOICE_SIMILARITY
        for i in range(len(embeddings))
        for j in range(i + 1, len(embeddings))
    )
