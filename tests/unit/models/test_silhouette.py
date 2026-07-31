from vox.models.silhouette import silhouette_score

_WELL_SEPARATED = [
    (1.0, 0.0),
    (0.99, 0.01),
    (0.0, 1.0),
    (0.01, 0.99),
]


class TestSilhouetteScore:
    def test_score_when_well_separated_then_close_to_one(self):
        score = silhouette_score(_WELL_SEPARATED, [0, 0, 1, 1])

        assert score > 0.9

    def test_score_when_groups_are_scrambled_then_much_lower(self):
        good = silhouette_score(_WELL_SEPARATED, [0, 0, 1, 1])
        scrambled = silhouette_score(_WELL_SEPARATED, [0, 1, 0, 1])

        assert scrambled < good

    def test_score_when_single_cluster_then_zero(self):
        assert silhouette_score(_WELL_SEPARATED, [0, 0, 0, 0]) == 0.0

    def test_score_when_every_point_alone_then_zero(self):
        assert silhouette_score(_WELL_SEPARATED, [0, 1, 2, 3]) == 0.0

    def test_score_when_empty_then_zero(self):
        assert silhouette_score([], []) == 0.0

    def test_score_when_three_clear_groups_then_high(self):
        points = [
            (1.0, 0.0, 0.0),
            (0.99, 0.01, 0.0),
            (0.0, 1.0, 0.0),
            (0.0, 0.99, 0.01),
            (0.0, 0.0, 1.0),
            (0.01, 0.0, 0.99),
        ]

        assert silhouette_score(points, [0, 0, 1, 1, 2, 2]) > 0.8
