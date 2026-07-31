import pytest

from vox.models.exceptions import ValidationError
from vox.models.voice_print import VoicePrint


class TestVoicePrint:
    def test_create_when_valid_then_fields_set(self):
        print_ = VoicePrint(name="Coco", embedding=(0.1, 0.2, 0.3))

        assert print_.name == "Coco"
        assert print_.embedding == (0.1, 0.2, 0.3)

    def test_create_when_blank_name_then_raises(self):
        with pytest.raises(ValidationError, match="name"):
            VoicePrint(name="  ", embedding=(0.1,))

    def test_create_when_empty_embedding_then_raises(self):
        with pytest.raises(ValidationError, match="embedding"):
            VoicePrint(name="Coco", embedding=())
