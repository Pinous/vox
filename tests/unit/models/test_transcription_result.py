from vox.models.segment import Segment
from vox.models.transcription_result import TranscriptionResult
from vox.models.word import Word


class TestTranscriptionResult:
    def test_create_when_valid_then_fields_set(self):
        segment = Segment(start=0.0, end=1.0, text="hello")
        result = TranscriptionResult(
            text="hello",
            segments=(segment,),
            language="en",
        )

        assert result.text == "hello"
        assert result.segments == (segment,)
        assert result.language == "en"

    def test_create_when_no_words_then_words_is_none(self):
        segment = Segment(start=0.0, end=1.0, text="hello")
        result = TranscriptionResult(
            text="hello",
            segments=(segment,),
            language="en",
        )

        assert result.words is None

    def test_create_when_with_words_then_words_accessible(self):
        segment = Segment(start=0.0, end=1.0, text="hello world")
        word1 = Word(start=0.0, end=0.5, word="hello", probability=0.9)
        word2 = Word(start=0.5, end=1.0, word="world", probability=0.8)
        result = TranscriptionResult(
            text="hello world",
            segments=(segment,),
            language="en",
            words=(word1, word2),
        )

        assert result.words == (word1, word2)
        assert len(result.words) == 2
