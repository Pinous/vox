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


class CountingDiarizer:
    """Records every call and replays a canned probe, then a final pass."""

    def __init__(self, probe):
        self._probe = probe
        self.calls: list[int | None] = []

    def diarize(self, audio_path, num_speakers):
        self.calls.append(num_speakers)
        return self._probe


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

    def test_diarize_when_single_turn_then_probe_returned_as_is(self):
        turns = (SpeakerTurn(start=0.0, end=10.0, speaker="SPEAKER_00"),)
        auto = AutoSpeakerCountDiarizer(FakeDiarizer(turns), FakeVoicePrintExtractor())

        assert auto.diarize(_AUDIO, None) == turns

    def test_diarize_when_auto_then_reruns_with_the_estimated_count(self):
        inner = CountingDiarizer(_THREE_LABELS)
        extractor = FakeVoicePrintExtractor(
            {
                (0.0, 10.0): (1.0, 0.0),
                (10.0, 20.0): (0.0, 1.0),
                (20.0, 30.0): (0.99, 0.01),
            }
        )
        auto = AutoSpeakerCountDiarizer(inner, extractor)

        auto.diarize(_AUDIO, None)

        assert inner.calls == [None, 2]

    def test_diarize_when_all_one_voice_then_final_pass_asks_for_one(self):
        inner = CountingDiarizer(_THREE_LABELS)
        extractor = FakeVoicePrintExtractor(
            {
                (0.0, 10.0): (1.0, 0.0),
                (10.0, 20.0): (0.999, 0.01),
                (20.0, 30.0): (0.998, 0.02),
            }
        )
        auto = AutoSpeakerCountDiarizer(inner, extractor)

        auto.diarize(_AUDIO, None)

        assert inner.calls == [None, 1]

    def test_diarize_when_many_labels_then_sample_is_capped(self):
        many = tuple(
            SpeakerTurn(start=float(i), end=float(i) + 1, speaker=f"SPEAKER_{i:03d}")
            for i in range(300)
        )
        extractor = FakeVoicePrintExtractor()
        auto = AutoSpeakerCountDiarizer(
            CountingDiarizer(many), extractor, sample_size=24
        )

        auto.diarize(_AUDIO, None)

        assert len(extractor.extract_calls) == 24

    def test_diarize_when_auto_then_samples_the_longest_turns(self):
        turns = (
            SpeakerTurn(start=0.0, end=1.0, speaker="SPEAKER_00"),
            SpeakerTurn(start=10.0, end=40.0, speaker="SPEAKER_01"),
            SpeakerTurn(start=50.0, end=90.0, speaker="SPEAKER_02"),
        )
        extractor = FakeVoicePrintExtractor()
        auto = AutoSpeakerCountDiarizer(
            CountingDiarizer(turns), extractor, sample_size=2
        )

        auto.diarize(_AUDIO, None)

        spans = [c[1:] for c in extractor.extract_calls]
        assert (50.0, 90.0) in spans
        assert (10.0, 40.0) in spans
        assert (0.0, 1.0) not in spans
