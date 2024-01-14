import traceback
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Collection, Iterable, Optional

import click
from pydantic.dataclasses import dataclass
from tqdm import tqdm

from monopoly.processors import detect_processor


@dataclass
class Result:
    """
    Stores information about processed bank statement
    """

    source_file_name: str
    target_file_name: Optional[str] = None
    error_info: Optional[dict[str, str]] = None


@dataclass
class Report:
    """
    A helper class for parsing and displaying processed bank statements.
    """

    results: list[Result]

    @property
    def processed_results(self) -> list[Result]:
        return sorted(
            [r for r in self.results if not r.error_info],
            key=lambda x: x.source_file_name,
        )

    @property
    def errored_results(self) -> list[Result]:
        return sorted(
            [r for r in self.results if r.error_info], key=lambda x: x.source_file_name
        )

    @property
    def number_processed(self) -> int:
        return len(self.processed_results)

    @property
    def number_errored(self) -> int:
        return len(self.errored_results)

    def display_report(self) -> None:
        """
        Parses all results, displaying the number of successfully
        processed statements and any errors.
        """
        if self.number_errored > 0:
            error_msg = (
                f"{self.number_errored} statement(s) had errors while processing"
            )
            click.echo(click.style(error_msg, fg="red", bold=True))
        if self.number_processed > 0:
            changed_msg = f"{self.number_processed} statement(s) processed"
            click.echo(click.style(changed_msg, bold=True))

        for res in self.errored_results:
            click.echo(
                click.style(
                    f"{res.source_file_name} -- "
                    f"{res.error_info['message'][:120]}",  # type: ignore
                    fg="red",
                )
            )

        for res in self.processed_results:
            click.echo(f"{res.source_file_name} -> {res.target_file_name}")


def process_statement(
    file: Path, output_directory: Optional[Path], print_df: bool
) -> Optional[Result]:
    """
    Extracts, transforms, and loads transactions from bank statements.

    Parameters:
        file: The path to the bank statement file.
        output_directory: The directory to save the processed statement.
            Defaults to the parent directory of the input file if not provided.
        print_df: If True, the transformed DataFrame is printed to the console
            in a tabular format. No file is generated in this case.

    Returns:
        Optional[Result]: If print_df is False, returns a Result object containing
        information about the processed statement. If an error occurs during processing,
        returns a Result object with error information.
    """

    try:
        processor = detect_processor(file)
        statement = processor.extract()
        transformed_df = processor.transform(statement)

        if print_df:
            click.echo(f"{file.name}")
            click.echo(transformed_df.to_markdown(tablefmt="psql", numalign="right"))
            click.echo()
            return None

        # saves processed statements to the same directory by default
        if not output_directory:
            output_directory = file.parent

        output_file = processor.load(transformed_df, statement, output_directory)
        return Result(file.name, output_file.name)

    except Exception as err:  # pylint: disable=broad-exception-caught
        error_info = {
            "message": f"{type(err).__name__}: {str(err)}",
            "traceback": traceback.format_exc(),
        }
        return Result(file.name, error_info=error_info)


def run(
    input_files: Collection[Path],
    output_directory: Optional[Path] = None,
    print_df: bool = False,
):
    """
    Process a collection of input files concurrently

    If any statements are processed successfully or encounter errors, a Report object
    is created and its display_report() method is called to provide a summary
    of the processing outcomes.
    """
    with ProcessPoolExecutor() as executor:
        results = list(
            tqdm(
                executor.map(
                    process_statement,
                    input_files,
                    [output_directory] * len(input_files),
                    [print_df] * len(input_files),
                ),
                total=len(input_files),
                desc="Processing statements",
                leave=False,
                delay=0.5,
                ncols=80,
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}",
            )
        )

    if any(results):
        # filter out null values, for cases where print_df is True
        # and processing errors occur to avoid pydantic validation errors
        report = Report([res for res in results if res])
        report.display_report()


def get_statement_paths(files: Iterable[Path]) -> set[Path]:
    """
    Recursively collects paths to PDF files from a given collection of paths.
    """
    matched_files = set()
    for path in files:
        if path.is_file() and str(path).endswith(".pdf"):
            matched_files.add(path)

        if path.is_dir():
            matched_files |= get_statement_paths(path.iterdir())

    return matched_files


@click.command()
@click.version_option(package_name="monopoly-sg")
@click.argument(
    "files",
    nargs=-1,
    type=click.Path(exists=True, allow_dash=True, resolve_path=True, path_type=Path),
)
@click.option(
    "-o",
    "--output",
    type=click.Path(exists=True, allow_dash=True, resolve_path=True, path_type=Path),
    help="Specify output folder",
)
@click.option(
    "-p",
    "--pprint",
    is_flag=True,
    help="Print the processed statement(s)",
)
@click.pass_context
def monopoly(ctx: click.Context, files: list[Path], output: Path, pprint: bool):
    """
    Monopoly helps convert your bank statements from PDF to CSV.

    A file or directory can be passed in via the FILES argument
    """
    if files:
        matched_files = get_statement_paths(files)

        if matched_files:
            run(matched_files, output, pprint)
            ctx.exit(0)

        else:
            click.echo(
                click.style("Could not find .pdf files", fg="yellow", bold=True),
                err=True,
            )
            ctx.exit(1)
    else:
        show_welcome_message()


def show_welcome_message():
    art = r"""
     __  __                               _
    |  \/  | ___  _ __   ___  _ __   ___ | |_   _
    | |\/| |/ _ \| '_ \ / _ \| '_ \ / _ \| | | | |
    | |  | | (_) | | | | (_) | |_) | (_) | | |_| |
    |_|  |_|\___/|_| |_|\___/| .__/ \___/|_|\__, |
                             |_|            |___/
    """

    click.echo(art)
    message = "Monopoly helps convert your bank statements from PDF to CSV"
    click.echo(message)
    commands = [
        (
            "monopoly .",
            "process all statements nested in current dir",
        ),
        (
            "monopoly path/to/file.pdf",
            "process a specific bank statement",
        ),
        (
            "monopoly . --output <dir>",
            "saves all results to a specific directory",
        ),
        (
            "monopoly . --pprint",
            "prints results instead of saving them",
        ),
        (
            "monopoly --help",
            "show more options and other usage information",
        ),
    ]
    margin = max(len(cmd) for cmd, _ in commands)
    for cmd, desc in commands:
        styled_cmd = click.style(
            text=f"{cmd}{' ' * (margin - len(cmd))}",
            fg="white",
            bg="bright_black",
            bold=True,
        )
        click.echo(message=f"    {styled_cmd} {desc}")
    click.echo()
