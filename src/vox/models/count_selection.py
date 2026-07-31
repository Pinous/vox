# 1.0 keeps the plain best-scoring count. Lower values accept a finer split
# whose score stays within `tolerance` of the best one: it recovers speakers
# the silhouette tends to merge, at the cost of inventing thin extra ones.
# Measured at 0.70 on a real 3-speaker recording: the count became right while
# the third label held 2 turns out of 609, and 2-speaker files drifted to 3-4.
DEFAULT_TOLERANCE = 1.0


def pick_speaker_count(
    scores: dict[int, float],
    tolerance: float = DEFAULT_TOLERANCE,
) -> int:
    if not scores:
        return 1
    best = max(scores.values())
    if best <= 0:
        return 1
    floor = tolerance * best
    return max(count for count, score in scores.items() if score >= floor)
