_AUTH_ERROR_MARKERS = (
    "sign in",
    "login",
    "cookies",
    "private video",
    "members-only",
    "age-restricted",
    "empty media response",
    "not a bot",
    "authentication",
)

_ALTERNATIVE_BROWSERS = "safari, firefox, edge, brave"


def format_download_failure(
    stderr: str,
    used_cookies: bool,
    browser: str = "chrome",
) -> str:
    return f"yt-dlp failed: {stderr}{_auth_hint(stderr, used_cookies, browser)}"


def _auth_hint(stderr: str, used_cookies: bool, browser: str) -> str:
    if not _looks_like_auth_error(stderr):
        return ""
    if used_cookies:
        return (
            f"\nHint: {browser} cookies were sent but rejected. "
            f"Sign in to the site in {browser}, "
            f"or pick another with --browser ({_ALTERNATIVE_BROWSERS})."
        )
    return (
        "\nHint: this source needs authentication. "
        "Drop --no-cookies to reuse your browser session."
    )


def _looks_like_auth_error(stderr: str) -> bool:
    lowered = stderr.lower()
    return any(marker in lowered for marker in _AUTH_ERROR_MARKERS)
