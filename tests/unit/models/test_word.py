import pytest

from vox.models.exceptions import ValidationError
from vox.models.word import Word


class TestWord:
    def test_create_when_valid_then_fields_set(self):
        word = Word(start=0.0, end=0.5, word="hello", probability=0.95)

        assert word.start == 0.0
        assert word.end == 0.5
        assert word.word == "hello"
        assert word.probability == 0.95

    def test_create_when_probability_negative_then_raises(self):
        with pytest.raises(ValidationError, match="probability"):
            Word(start=0.0, end=0.5, word="hello", probability=-0.1)

    def test_create_when_probability_over_one_then_raises(self):
        with pytest.raises(ValidationError, match="probability"):
            Word(start=0.0, end=0.5, word="hello", probability=1.1)

    def test_create_when_valid_probability_then_accepted(self):
        word_zero = Word(start=0.0, end=0.5, word="a", probability=0.0)
        word_one = Word(start=0.0, end=0.5, word="b", probability=1.0)

        assert word_zero.probability == 0.0
        assert word_one.probability == 1.0
