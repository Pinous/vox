import json
from pathlib import Path

from vox.models.voice_print import VoicePrint


class JsonVoicePrintStore:
    def __init__(self, path: Path | None = None):
        self._path = path or Path.home() / ".vox" / "voiceprints.json"

    def save(self, voice_print: VoicePrint) -> None:
        prints = {p.name: list(p.embedding) for p in self.load_all()}
        prints[voice_print.name] = list(voice_print.embedding)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(prints, indent=2), encoding="utf-8")

    def load_all(self) -> tuple[VoicePrint, ...]:
        if not self._path.exists():
            return ()
        raw = json.loads(self._path.read_text(encoding="utf-8"))
        return tuple(
            VoicePrint(name=name, embedding=tuple(embedding))
            for name, embedding in raw.items()
        )
