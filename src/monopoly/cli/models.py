from dataclasses import dataclass, field
from pathlib import Path

import click


@dataclass
class RunConfig:
    output_directory: Path | None = None
    pprint: bool = False
    safety_check: bool = True
    single_process: bool = False
    use_ocr: bool = False
    verbose: bool = False
    preserve_filename: bool = False


@dataclass
class TqdmSettings:
    """Configuration for a tqdm progress bar."""

    total: int
    desc: str = "Processing statements"
    leave: bool = False
    delay: float = 0.2
    ncols: int = 80
    bar_format: str = "{l_bar}{bar}| {n_fmt}/{total_fmt}"


@dataclass
class Result:
    """Stores information about processed bank statement."""

    source_file_name: str
    target_file_name: str | None = None
    error_info: dict[str, str] = field(default_factory=dict)


@dataclass
class Report:
    """A helper class for parsing and displaying processed bank statements."""

    results: list[Result]

    @property
    def processed_results(self) -> list[Result]:
        return sorted(
            [r for r in self.results if not r.error_info],
            key=lambda x: x.source_file_name,
        )

    @property
    def errored_results(self) -> list[Result]:
        return sorted([r for r in self.results if r.error_info], key=lambda x: x.source_file_name)

    @property
    def number_processed(self) -> int:
        return len(self.processed_results)

    @property
    def number_errored(self) -> int:
        return len(self.errored_results)

    def display_report(self, *_, verbose=False) -> None:
        """Parse all results, displaying the number of successfully processed statements and any errors."""
        for res in self.processed_results:
            click.echo(f"{res.source_file_name} -> {res.target_file_name}")

        if self.number_errored > 0:
            error_msg = f"{self.number_errored} statement(s) had errors while processing"
            click.echo(click.style(error_msg, fg="red", bold=True))
        if self.number_processed > 0:
            changed_msg = f"{self.number_processed} statement(s) processed"
            click.echo(click.style(changed_msg, bold=True))

        for res in self.errored_results:
            error_msg = res.error_info["message"]
            if verbose:
                error_msg = res.error_info["traceback"]
            click.echo(
                click.style(
                    f"{res.source_file_name} -- {error_msg}",
                    fg="red",
                )
            )
