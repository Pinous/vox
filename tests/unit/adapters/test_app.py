from importlib.metadata import version

from click.testing import CliRunner

from vox.adapters.cli.app import main


class TestVersionOption:
    def test_main_when_version_flag_then_exits_successfully(self):
        result = CliRunner().invoke(main, ["--version"])

        assert result.exit_code == 0

    def test_main_when_version_flag_then_outputs_installed_version(self):
        result = CliRunner().invoke(main, ["--version"])

        assert version("vox-transcribe") in result.output

    def test_main_when_version_flag_then_not_routed_to_transcribe(self):
        result = CliRunner().invoke(main, ["--version"])

        assert "Source must not be empty" not in result.output


def _option_names(command) -> set[str]:
    return {opt for param in command.params for opt in param.opts}


class TestCookieOptions:
    def test_transcribe_when_inspected_then_exposes_browser_option(self):
        assert "--browser" in _option_names(main.commands["transcribe"])

    def test_transcribe_when_inspected_then_exposes_no_cookies_option(self):
        assert "--no-cookies" in _option_names(main.commands["transcribe"])

    def test_channel_when_inspected_then_exposes_browser_option(self):
        assert "--browser" in _option_names(main.commands["channel"])
