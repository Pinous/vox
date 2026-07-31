from vox.models.clustering import cluster_embeddings

_TWO_GROUPS = [
    (1.0, 0.0),
    (0.99, 0.01),
    (0.0, 1.0),
    (0.01, 0.99),
]


def _groups(labels: list[int]) -> set[frozenset[int]]:
    groups: dict[int, set[int]] = {}
    for index, label in enumerate(labels):
        groups.setdefault(label, set()).add(index)
    return {frozenset(g) for g in groups.values()}


class TestClusterEmbeddings:
    def test_cluster_when_two_obvious_groups_then_splits_them(self):
        labels = cluster_embeddings(_TWO_GROUPS, n_clusters=2)

        assert _groups(labels) == {frozenset({0, 1}), frozenset({2, 3})}

    def test_cluster_when_one_cluster_then_all_together(self):
        labels = cluster_embeddings(_TWO_GROUPS, n_clusters=1)

        assert len(set(labels)) == 1

    def test_cluster_when_as_many_clusters_as_points_then_all_separate(self):
        labels = cluster_embeddings(_TWO_GROUPS, n_clusters=4)

        assert len(set(labels)) == 4

    def test_cluster_when_more_clusters_than_points_then_capped(self):
        labels = cluster_embeddings(_TWO_GROUPS, n_clusters=99)

        assert len(set(labels)) == 4

    def test_cluster_when_empty_then_empty(self):
        assert cluster_embeddings([], n_clusters=2) == []

    def test_cluster_when_three_groups_then_splits_them(self):
        points = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)]

        labels = cluster_embeddings(points, n_clusters=3)

        assert len(set(labels)) == 3

    def test_cluster_when_called_then_labels_are_contiguous_from_zero(self):
        labels = cluster_embeddings(_TWO_GROUPS, n_clusters=2)

        assert sorted(set(labels)) == [0, 1]
