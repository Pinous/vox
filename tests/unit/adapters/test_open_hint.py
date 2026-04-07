from vox.adapters.cli.open_hint import format_open_hint


class TestFormatOpenHint:
    def test_format_when_srt_path_then_open_command_with_path(self):
        result = format_open_hint("/tmp/audio.srt")

        assert result == "-> open /tmp/audio.srt"

    def test_format_when_path_with_spaces_then_quoted(self):
        result = format_open_hint("/tmp/my audio.srt")

        assert result == "-> open '/tmp/my audio.srt'"

    def test_format_when_path_with_single_quote_then_escaped(self):
        result = format_open_hint("/tmp/it's.srt")

        assert "/tmp/it" in result
        assert "open" in result
