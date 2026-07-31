from vox.models.voice_matching import Embedding, cosine_similarity


def cluster_embeddings(
    embeddings: list[Embedding],
    n_clusters: int,
) -> list[int]:
    groups = [[i] for i in range(len(embeddings))]
    target = max(1, min(n_clusters, len(groups)))
    while len(groups) > target:
        left, right = _closest_pair(groups, embeddings)
        groups[left].extend(groups.pop(right))
    return _to_labels(groups, len(embeddings))


def _closest_pair(
    groups: list[list[int]],
    embeddings: list[Embedding],
) -> tuple[int, int]:
    best = (-2.0, 0, 1)
    for i in range(len(groups)):
        for j in range(i + 1, len(groups)):
            score = _average_linkage(groups[i], groups[j], embeddings)
            if score > best[0]:
                best = (score, i, j)
    return best[1], best[2]


def _average_linkage(
    left: list[int],
    right: list[int],
    embeddings: list[Embedding],
) -> float:
    scores = [
        cosine_similarity(embeddings[a], embeddings[b]) for a in left for b in right
    ]
    return sum(scores) / len(scores)


def _to_labels(groups: list[list[int]], size: int) -> list[int]:
    labels = [0] * size
    for label, group in enumerate(groups):
        for index in group:
            labels[index] = label
    return labels
