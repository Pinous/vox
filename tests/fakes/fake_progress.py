class FakeProgressReporter:
    def __init__(self):
        self.steps: list[str] = []
        self.finished: bool = False

    def start(self, label: str) -> None:
        self.steps.append(f"start:{label}")

    def update(self, label: str) -> None:
        self.steps.append(f"update:{label}")

    def finish(self) -> None:
        self.finished = True
