from typing import Protocol

from vox.models.voice_print import VoicePrint


class VoicePrintStore(Protocol):
    def save(self, voice_print: VoicePrint) -> None: ...

    def load_all(self) -> tuple[VoicePrint, ...]: ...
