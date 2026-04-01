import pytest

from vox.models.exceptions import ValidationError
from vox.models.language import Language


class TestLanguage:
    def test_create_when_valid_code_then_lowercase(self):
        result = Language.from_string("fr")

        assert result.code == "fr"

    def test_create_when_auto_then_code_is_auto(self):
        result = Language.from_string("auto")

        assert result.code == "auto"

    def test_create_when_uppercase_then_normalized(self):
        result = Language.from_string("EN")

        assert result.code == "en"

    def test_create_when_invalid_code_then_raises(self):
        with pytest.raises(ValidationError, match="language"):
            Language.from_string("zz")

    def test_create_when_empty_then_raises(self):
        with pytest.raises(ValidationError, match="empty"):
            Language.from_string("")

    def test_create_when_newly_added_code_then_accepted(self):
        result = Language.from_string("fa")

        assert result.code == "fa"
