import os

_SPARE_CORES = 2
_MIN_THREADS = 2


def default_num_threads() -> int:
    return choose_num_threads(os.cpu_count())


def choose_num_threads(logical_cores: int | None) -> int:
    if not logical_cores:
        return _MIN_THREADS
    return max(_MIN_THREADS, logical_cores - _SPARE_CORES)
