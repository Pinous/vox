from vox.adapters.cpu_threads import choose_num_threads


class TestChooseNumThreads:
    def test_choose_when_ten_cores_then_uses_eight(self):
        assert choose_num_threads(logical_cores=10) == 8

    def test_choose_when_many_cores_then_leaves_two_spare(self):
        assert choose_num_threads(logical_cores=16) == 14

    def test_choose_when_four_cores_then_two(self):
        assert choose_num_threads(logical_cores=4) == 2

    def test_choose_when_three_cores_then_stays_above_one(self):
        assert choose_num_threads(logical_cores=3) == 2

    def test_choose_when_two_cores_then_stays_above_one(self):
        assert choose_num_threads(logical_cores=2) == 2

    def test_choose_when_single_core_then_stays_above_one(self):
        assert choose_num_threads(logical_cores=1) == 2

    def test_choose_when_unknown_then_stays_above_one(self):
        assert choose_num_threads(logical_cores=None) == 2
