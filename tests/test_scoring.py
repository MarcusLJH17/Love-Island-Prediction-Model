from islandedge.scoring import FeatureRow, probability_distribution


def test_probability_distribution_sums_to_one():
    rows = [
        FeatureRow("A", 0.5, 0.4, 0.2, 0.1, 0.3, 0.2, 10, True),
        FeatureRow("B", -0.2, -0.1, 0.1, 0.0, -0.1, 0.0, 5, False),
    ]

    distribution = probability_distribution(rows)

    assert round(sum(distribution.values()), 6) == 1
    assert distribution["A"] > distribution["B"]
