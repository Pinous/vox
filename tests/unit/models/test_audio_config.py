import pytest

from vox.models.audio_config import AudioConfig
from vox.models.exceptions import ValidationError


class TestAudioConfigDefault:
    def test_default_when_created_then_has_correct_defaults(self):
        config = AudioConfig.default()

        assert config.remove_silence is True
        assert config.denoise is True
        assert config.normalize is True
        assert config.sample_rate == 16000
        assert config.channels == 1


class TestAudioConfigCreation:
    def test_create_when_custom_sample_rate_then_accepted(self):
        config = AudioConfig(sample_rate=44100)

        assert config.sample_rate == 44100

    def test_create_when_zero_sample_rate_then_raises(self):
        with pytest.raises(ValidationError):
            AudioConfig(sample_rate=0)

    def test_create_when_negative_sample_rate_then_raises(self):
        with pytest.raises(ValidationError):
            AudioConfig(sample_rate=-1)

    def test_create_when_channels_three_then_raises(self):
        with pytest.raises(ValidationError):
            AudioConfig(channels=3)

    def test_create_when_channels_one_then_accepted(self):
        config = AudioConfig(channels=1)

        assert config.channels == 1
