from vox.adapters.download_hint import format_download_failure


class TestFormatDownloadFailure:
    def test_format_when_plain_error_then_stderr_only(self):
        result = format_download_failure("ffmpeg not found", used_cookies=True)

        assert result == "yt-dlp failed: ffmpeg not found"

    def test_format_when_auth_error_and_cookies_unused_then_suggests_cookies(self):
        result = format_download_failure(
            "ERROR: Sign in to confirm you are not a bot",
            used_cookies=False,
        )

        assert "--no-cookies" in result

    def test_format_when_auth_error_and_cookies_used_then_suggests_other_browser(self):
        result = format_download_failure(
            "ERROR: Private video. Please sign in",
            used_cookies=True,
            browser="chrome",
        )

        assert "--browser" in result
        assert "chrome" in result

    def test_format_when_auth_error_then_keeps_original_stderr(self):
        result = format_download_failure("ERROR: login required", used_cookies=False)

        assert "login required" in result

    def test_format_when_instagram_empty_response_then_suggests_cookies(self):
        result = format_download_failure(
            "ERROR: empty media response",
            used_cookies=False,
        )

        assert "--no-cookies" in result

    def test_format_when_error_case_differs_then_still_detected(self):
        result = format_download_failure(
            "ERROR: COOKIES ARE REQUIRED", used_cookies=False
        )

        assert "--no-cookies" in result
