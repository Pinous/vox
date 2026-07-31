import pytest

from tests.fakes.fake_voice_print_extractor import FakeVoicePrintExtractor
from tests.fakes.fake_voice_print_store import FakeVoicePrintStore
from vox.models.exceptions import ValidationError
from vox.use_cases.enroll_speaker import EnrollSpeakerRequest, EnrollSpeakerUseCase


def _request(**overrides) -> EnrollSpeakerRequest:
    defaults = {
        "name": "Coco",
        "audio_path": "live.wav",
        "start": 10.0,
        "end": 25.0,
    }
    defaults.update(overrides)
    return EnrollSpeakerRequest(**defaults)


class TestEnrollSpeaker:
    def test_execute_when_valid_then_saves_print_under_name(self):
        store = FakeVoicePrintStore()
        use_case = EnrollSpeakerUseCase(FakeVoicePrintExtractor(), store)

        use_case.execute(_request())

        assert len(store.saved) == 1
        assert store.saved[0].name == "Coco"

    def test_execute_when_valid_then_extracts_requested_span(self):
        extractor = FakeVoicePrintExtractor()
        use_case = EnrollSpeakerUseCase(extractor, FakeVoicePrintStore())

        use_case.execute(_request(start=3.0, end=9.0))

        assert extractor.extract_calls[0][1:] == (3.0, 9.0)

    def test_execute_when_end_before_start_then_raises(self):
        use_case = EnrollSpeakerUseCase(
            FakeVoicePrintExtractor(), FakeVoicePrintStore()
        )

        with pytest.raises(ValidationError, match="end"):
            use_case.execute(_request(start=10.0, end=5.0))

    def test_execute_when_span_too_short_then_raises(self):
        use_case = EnrollSpeakerUseCase(
            FakeVoicePrintExtractor(), FakeVoicePrintStore()
        )

        with pytest.raises(ValidationError, match="second"):
            use_case.execute(_request(start=10.0, end=10.5))

    def test_execute_when_valid_then_returns_name_and_span(self):
        use_case = EnrollSpeakerUseCase(
            FakeVoicePrintExtractor(), FakeVoicePrintStore()
        )

        response = use_case.execute(_request())

        assert response.name == "Coco"
        assert response.seconds_used == 15.0
