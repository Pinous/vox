import shlex


def format_open_hint(path: str) -> str:
    return f"-> open {shlex.quote(path)}"
