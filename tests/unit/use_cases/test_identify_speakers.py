from pathlib import Path

from tests.fakes.fake_voice_print_extractor import FakeVoicePrintExtractor
from tests.fakes.fake_voice_print_store import FakeVoicePrintStore
from vox.models.speaker_turn import SpeakerTurn
from vox.models.voice_print import VoicePrint
from vox.use_cases.identify_speakers import IdentifySpeakersUseCase

_TURNS = (
    SpeakerTurn(start=0.0, end=10.0, speaker="SPEAKER_00"),
    SpeakerTurn(start=10.0, end=15.0, speaker="SPEAKER_01"),
)


class TestIdentifySpeakers:
    def test_execute_when_no_prints_then_empty_mapping(self):
        use_case = IdentifySpeakersUseCase(
            extractor=FakeVoicePrintExtractor(),
            store=FakeVoicePrintStore(),
        )

        assert use_case.execute(Path("a.wav"), _TURNS) == {}

    def test_execute_when_no_prints_then_extractor_not_called(self):
        extractor = FakeVoicePrintExtractor()
        use_case = IdentifySpeakersUseCase(extractor, FakeVoicePrintStore())

        use_case.execute(Path("a.wav"), _TURNS)

        assert extractor.extract_calls == []

    def test_execute_when_print_matches_then_label_mapped(self):
        store = FakeVoicePrintStore((VoicePrint(name="Coco", embedding=(1.0, 0.0)),))
        use_case = IdentifySpeakersUseCase(FakeVoicePrintExtractor(), store)

        mapping = use_case.execute(Path("a.wav"), _TURNS)

        assert mapping == {"SPEAKER_00": "Coco", "SPEAKER_01": "Coco"}

    def test_execute_when_print_too_far_then_not_mapped(self):
        store = FakeVoicePrintStore((VoicePrint(name="Coco", embedding=(0.0, 1.0)),))
        extractor = FakeVoicePrintExtractor({(0.0, 10.0): (1.0, 0.0)})
        use_case = IdentifySpeakersUseCase(extractor, store)

        mapping = use_case.execute(Path("a.wav"), _TURNS)

        assert "SPEAKER_00" not in mapping

    def test_execute_when_called_then_uses_longest_turn_per_speaker(self):
        store = FakeVoicePrintStore((VoicePrint(name="Coco", embedding=(1.0, 0.0)),))
        extractor = FakeVoicePrintExtractor()
        use_case = IdentifySpeakersUseCase(extractor, store)
        turns = (
            SpeakerTurn(start=0.0, end=2.0, speaker="SPEAKER_00"),
            SpeakerTurn(start=5.0, end=30.0, speaker="SPEAKER_00"),
        )

        use_case.execute(Path("a.wav"), turns)

        assert extractor.extract_calls == [(Path("a.wav"), 5.0, 30.0)]
