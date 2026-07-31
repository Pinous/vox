from vox.models.voice_matching import Embedding, cosine_similarity


def silhouette_score(
    embeddings: list[Embedding],
    labels: list[int],
) -> float:
    clusters = _group_indices(labels)
    if len(clusters) < 2:
        return 0.0
    scores = [
        _point_score(index, embeddings, clusters, labels)
        for index in range(len(embeddings))
    ]
    return sum(scores) / len(scores)


def _point_score(
    index: int,
    embeddings: list[Embedding],
    clusters: dict[int, list[int]],
    labels: list[int],
) -> float:
    own = clusters[labels[index]]
    if len(own) < 2:
        return 0.0
    inside = _mean_distance(index, own, embeddings, exclude_self=True)
    outside = min(
        _mean_distance(index, members, embeddings, exclude_self=False)
        for label, members in clusters.items()
        if label != labels[index]
    )
    spread = max(inside, outside)
    if spread == 0:
        return 0.0
    return (outside - inside) / spread


def _mean_distance(
    index: int,
    members: list[int],
    embeddings: list[Embedding],
    exclude_self: bool,
) -> float:
    others = [m for m in members if m != index] if exclude_self else members
    distances = [_distance(embeddings[index], embeddings[m]) for m in others]
    return sum(distances) / len(distances)


def _distance(left: Embedding, right: Embedding) -> float:
    return 1.0 - cosine_similarity(left, right)


def _group_indices(labels: list[int]) -> dict[int, list[int]]:
    clusters: dict[int, list[int]] = {}
    for index, label in enumerate(labels):
        clusters.setdefault(label, []).append(index)
    return clusters
