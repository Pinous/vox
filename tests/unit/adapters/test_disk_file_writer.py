import json

from vox.adapters.disk_file_writer import DiskFileWriter, _format_srt
from vox.models.segment import Segment
from vox.models.transcription_result import TranscriptionResult


def _make_result(segments, text="Hello world", language="en", words=None):
    return TranscriptionResult(
        text=text,
        segments=segments,
        language=language,
        words=words,
    )


class TestFormatSrt:
    def test_format_srt_when_single_segment_then_correct_format(self):
        result = _make_result(
            segments=(Segment(start=0.0, end=2.5, text="Hello world"),),
        )

        srt = _format_srt(result)

        assert srt == ("1\n00:00:00,000 --> 00:00:02,500\nHello world\n")

    def test_format_srt_when_multiple_segments_then_numbered(self):
        result = _make_result(
            segments=(
                Segment(start=0.0, end=2.5, text="Hello world"),
                Segment(start=3.0, end=5.8, text="How are you"),
                Segment(start=6.0, end=10.123, text="Fine thanks"),
            ),
        )

        srt = _format_srt(result)

        assert srt == (
            "1\n"
            "00:00:00,000 --> 00:00:02,500\n"
            "Hello world\n"
            "2\n"
            "00:00:03,000 --> 00:00:05,800\n"
            "How are you\n"
            "3\n"
            "00:00:06,000 --> 00:00:10,123\n"
            "Fine thanks\n"
        )

    def test_format_srt_when_over_one_hour_then_correct_timecode(self):
        result = _make_result(
            segments=(Segment(start=3661.5, end=3723.75, text="Late segment"),),
        )

        srt = _format_srt(result)

        assert srt == ("1\n01:01:01,500 --> 01:02:03,750\nLate segment\n")


class TestWriteTxt:
    def test_write_txt_when_called_then_writes_text(self, tmp_path):
        result = _make_result(
            segments=(Segment(start=0.0, end=1.0, text="Hi"),),
            text="Hello world",
        )
        path = tmp_path / "output.txt"
        writer = DiskFileWriter()

        writer.write_txt(result, path)

        assert path.read_text(encoding="utf-8") == "Hello world"


class TestWriteJson:
    def test_write_json_when_called_then_valid_json(self, tmp_path):
        result = _make_result(
            segments=(Segment(start=0.0, end=2.5, text="Hello world"),),
            text="Hello world",
            language="en",
        )
        path = tmp_path / "output.json"
        writer = DiskFileWriter()

        writer.write_json(result, path)

        parsed = json.loads(path.read_text(encoding="utf-8"))
        assert parsed["text"] == "Hello world"
        assert parsed["language"] == "en"
        assert len(parsed["segments"]) == 1
        assert parsed["segments"][0]["start"] == 0.0
        assert parsed["segments"][0]["end"] == 2.5
        assert parsed["segments"][0]["text"] == "Hello world"
        assert parsed["words"] is None
