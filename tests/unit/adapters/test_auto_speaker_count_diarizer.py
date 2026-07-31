from pathlib import Path

from tests.fakes.fake_diarizer import FakeDiarizer
from tests.fakes.fake_voice_print_extractor import FakeVoicePrintExtractor
from vox.adapters.auto_speaker_count_diarizer import AutoSpeakerCountDiarizer
from vox.models.speaker_turn import SpeakerTurn

_AUDIO = Path("live.wav")

_THREE_LABELS = (
    SpeakerTurn(start=0.0, end=10.0, speaker="SPEAKER_00"),
    SpeakerTurn(start=10.0, end=20.0, speaker="SPEAKER_01"),
    SpeakerTurn(start=20.0, end=30.0, speaker="SPEAKER_02"),
)


def _labels(turns) -> list[str]:
    return [t.speaker for t in turns]


class TestAutoSpeakerCountDiarizer:
    def test_diarize_when_count_forced_then_delegates_untouched(self):
        inner = FakeDiarizer(_THREE_LABELS)
        auto = AutoSpeakerCountDiarizer(inner, FakeVoicePrintExtractor())

        auto.diarize(_AUDIO, 3)

        assert inner.diarize_called_with == (_AUDIO, 3)

    def test_diarize_when_count_forced_then_no_embedding_computed(self):
        extractor = FakeVoicePrintExtractor()
        auto = AutoSpeakerCountDiarizer(FakeDiarizer(_THREE_LABELS), extractor)

        auto.diarize(_AUDIO, 3)

        assert extractor.extract_calls == []

    def test_diarize_when_single_label_then_returned_as_is(self):
        turns = (SpeakerTurn(start=0.0, end=10.0, speaker="SPEAKER_00"),)
        auto = AutoSpeakerCountDiarizer(FakeDiarizer(turns), FakeVoicePrintExtractor())

        assert auto.diarize(_AUDIO, None) == turns

    def test_diarize_when_labels_are_distinct_voices_then_all_kept(self):
        extractor = FakeVoicePrintExtractor(
            {
                (0.0, 10.0): (1.0, 0.0, 0.0),
                (10.0, 20.0): (0.0, 1.0, 0.0),
                (20.0, 30.0): (0.0, 0.0, 1.0),
            }
        )
        auto = AutoSpeakerCountDiarizer(FakeDiarizer(_THREE_LABELS), extractor)

        assert len(set(_labels(auto.diarize(_AUDIO, None)))) == 3

    def test_diarize_when_two_labels_are_the_same_voice_then_merged(self):
        extractor = FakeVoicePrintExtractor(
            {
                (0.0, 10.0): (1.0, 0.0),
                (10.0, 20.0): (0.0, 1.0),
                (20.0, 30.0): (0.99, 0.01),
            }
        )
        auto = AutoSpeakerCountDiarizer(FakeDiarizer(_THREE_LABELS), extractor)

        result = _labels(auto.diarize(_AUDIO, None))

        assert len(set(result)) == 2
        assert result[0] == result[2]
        assert result[0] != result[1]

    def test_diarize_when_all_labels_same_voice_then_collapses_to_one(self):
        extractor = FakeVoicePrintExtractor(
            {
                (0.0, 10.0): (1.0, 0.0),
                (10.0, 20.0): (0.999, 0.01),
                (20.0, 30.0): (0.998, 0.02),
            }
        )
        auto = AutoSpeakerCountDiarizer(FakeDiarizer(_THREE_LABELS), extractor)

        assert len(set(_labels(auto.diarize(_AUDIO, None)))) == 1

    def test_diarize_when_auto_then_uses_longest_turn_of_each_label(self):
        extractor = FakeVoicePrintExtractor()
        turns = (
            SpeakerTurn(start=0.0, end=2.0, speaker="SPEAKER_00"),
            SpeakerTurn(start=5.0, end=30.0, speaker="SPEAKER_00"),
            SpeakerTurn(start=30.0, end=40.0, speaker="SPEAKER_01"),
        )
        auto = AutoSpeakerCountDiarizer(FakeDiarizer(turns), extractor)

        auto.diarize(_AUDIO, None)

        spans = [call[1:] for call in extractor.extract_calls]
        assert (5.0, 30.0) in spans
        assert (0.0, 2.0) not in spans
