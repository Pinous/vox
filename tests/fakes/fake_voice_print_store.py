from vox.models.voice_print import VoicePrint


class FakeVoicePrintStore:
    def __init__(self, prints: tuple[VoicePrint, ...] = ()):
        self._prints = list(prints)
        self.saved: list[VoicePrint] = []

    def save(self, voice_print: VoicePrint) -> None:
        self.saved.append(voice_print)
        self._prints = [p for p in self._prints if p.name != voice_print.name]
        self._prints.append(voice_print)

    def load_all(self) -> tuple[VoicePrint, ...]:
        return tuple(self._prints)
