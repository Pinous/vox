from vox.adapters.json_voice_print_store import JsonVoicePrintStore
from vox.models.voice_print import VoicePrint


class TestJsonVoicePrintStore:
    def test_load_all_when_no_file_then_empty(self, tmp_path):
        store = JsonVoicePrintStore(tmp_path / "prints.json")

        assert store.load_all() == ()

    def test_save_then_load_all_returns_print(self, tmp_path):
        store = JsonVoicePrintStore(tmp_path / "prints.json")

        store.save(VoicePrint(name="Coco", embedding=(0.1, 0.2)))

        loaded = store.load_all()
        assert len(loaded) == 1
        assert loaded[0].name == "Coco"
        assert loaded[0].embedding == (0.1, 0.2)

    def test_save_when_same_name_twice_then_overwrites(self, tmp_path):
        store = JsonVoicePrintStore(tmp_path / "prints.json")

        store.save(VoicePrint(name="Coco", embedding=(0.1,)))
        store.save(VoicePrint(name="Coco", embedding=(0.9,)))

        loaded = store.load_all()
        assert len(loaded) == 1
        assert loaded[0].embedding == (0.9,)

    def test_save_when_different_names_then_both_kept(self, tmp_path):
        store = JsonVoicePrintStore(tmp_path / "prints.json")

        store.save(VoicePrint(name="Coco", embedding=(0.1,)))
        store.save(VoicePrint(name="Leslie", embedding=(0.2,)))

        assert {p.name for p in store.load_all()} == {"Coco", "Leslie"}
