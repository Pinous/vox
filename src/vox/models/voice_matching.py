import math

from vox.models.voice_print import VoicePrint

Embedding = tuple[float, ...]


def cosine_similarity(left: Embedding, right: Embedding) -> float:
    norm = _norm(left) * _norm(right)
    if norm == 0:
        return 0.0
    return sum(a * b for a, b in zip(left, right, strict=True)) / norm


def match_speakers(
    label_embeddings: dict[str, Embedding],
    prints: tuple[VoicePrint, ...],
    threshold: float,
) -> dict[str, str]:
    if not prints:
        return {}
    mapping = {}
    for label, embedding in label_embeddings.items():
        name = _best_match(embedding, prints, threshold)
        if name is not None:
            mapping[label] = name
    return mapping


def _best_match(
    embedding: Embedding,
    prints: tuple[VoicePrint, ...],
    threshold: float,
) -> str | None:
    scored = [(cosine_similarity(embedding, p.embedding), p.name) for p in prints]
    best_score, best_name = max(scored)
    if best_score < threshold:
        return None
    return best_name


def _norm(vector: Embedding) -> float:
    return math.sqrt(sum(v * v for v in vector))
