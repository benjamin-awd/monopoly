"""Unit tests for `monopoly.cli.models.Report.display_report`."""

from monopoly.cli import cli as cli_module
from monopoly.cli.models import Report, Result, RunConfig


def _errored_result() -> Result:
    return Result(
        "statement.pdf",
        error_info={"message": "boom", "traceback": "TRACEBACK-LINE"},
    )


def test_display_report_shows_message_by_default(capsys):
    Report([_errored_result()]).display_report()
    out = capsys.readouterr().out
    assert "statement.pdf -- boom" in out
    assert "TRACEBACK-LINE" not in out


def test_display_report_verbose_shows_traceback(capsys):
    Report([_errored_result()]).display_report(verbose=True)
    out = capsys.readouterr().out
    assert "TRACEBACK-LINE" in out


def test_run_forwards_verbose_flag_to_report(capsys, monkeypatch):
    # Regression test: run() passed config.verbose positionally, where it
    # was swallowed by a stray *args parameter, so --verbose never showed
    # tracebacks for failed statements.
    def fake_get_results(_files, _config):
        return [_errored_result()]

    monkeypatch.setattr(cli_module, "get_results", fake_get_results)
    cli_module.run([], RunConfig(verbose=True))
    out = capsys.readouterr().out
    assert "TRACEBACK-LINE" in out
