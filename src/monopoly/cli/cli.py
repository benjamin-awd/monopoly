import traceback
from collections.abc import Collection, Iterable
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from functools import partial
from pathlib import Path

import click
from tabulate import tabulate
from tqdm import tqdm

from monopoly.cli.models import Report, Result, RunConfig, TqdmSettings
from monopoly.log import file_context, setup_logs, worker_log_setup


def process_statement(file: Path, config: RunConfig) -> Result | None:
    """Extract, transform, and load transactions from bank statements."""
    # The file_context should only be set and displayed when the verbose formatter is active,
    # but setting an additional gate here to adopt a slightly stricter security posture.
    if config.verbose:
        file_context.set(file.name)

    # Lazily importing here prevents from CLI from having a "slow" start
    from monopoly.banks import BankDetector, banks
    from monopoly.generic import GenericBank
    from monopoly.pdf import PdfDocument, PdfParser
    from monopoly.pipeline import Pipeline

    try:
        document = PdfDocument(file)
        document.unlock_document()

        if config.use_ocr:
            document = PdfParser.apply_ocr(document)

        analyzer = BankDetector(document)
        bank = analyzer.detect_bank(banks) or GenericBank
        parser = PdfParser(bank, document)
        pipeline = Pipeline(parser)

        statement = pipeline.extract(safety_check=config.safety_check)
        transactions = pipeline.transform(statement)

        if config.pprint:
            pprint_transactions(transactions, statement, file)
            # don't load to CSV if pprint
            return None

        # saves processed statements to the same directory by default
        if not config.output_directory:
            config.output_directory = file.parent

        output_file = pipeline.load(
            transactions,
            statement,
            config.output_directory,
            preserve_filename=config.preserve_filename,
        )
        return Result(file.name, output_file.name)

    # ruff: noqa: BLE001
    except Exception as err:
        error_info = {
            "message": f"{type(err).__name__}: {err!s}",
            "traceback": traceback.format_exc(),
        }
        return Result(file.name, error_info=error_info)


def pprint_transactions(transactions: list, statement, file: Path) -> None:
    """Print transactions in a markdown style tabular format."""
    click.echo(f"{file.name}")
    transactions_as_dict = [transaction.as_raw_dict() for transaction in transactions]
    headers = {col: col for col in statement.columns}
    click.echo(
        tabulate(
            transactions_as_dict,
            headers=headers,
            tablefmt="psql",
            numalign="right",
        )
    )
    click.echo()


def get_results(input_files: Collection[Path], config: RunConfig):
    tqdm_settings = asdict(TqdmSettings(len(input_files)))
    processor = partial(process_statement, config=config)

    if config.single_process or len(input_files) == 1:
        return [processor(file) for file in tqdm(input_files, **tqdm_settings)]

    initializer = partial(worker_log_setup, verbose=config.verbose)

    with ProcessPoolExecutor(initializer=initializer) as executor:
        return list(
            tqdm(
                executor.map(processor, input_files),
                **tqdm_settings,
            )
        )


def run(input_files: Collection[Path], config: RunConfig):
    """
    Process a collection of input files concurrently.

    If any statements are processed successfully or encounter errors, a Report object
    is created and its display_report() method is called to provide a summary
    of the processing outcomes.
    """
    results = get_results(input_files, config)

    if any(results):
        # filter out null values to avoid pydantic validation errors,
        # for cases where print_df is True and processing errors occur
        report = Report([res for res in results if res])
        report.display_report(config.verbose)


def get_statement_paths(files: Iterable[Path]) -> set[Path]:
    """Recursively collects paths to PDF files from a given collection of paths."""
    matched_files = set()
    for path in files:
        if path.is_file() and str(path).endswith(".pdf"):
            matched_files.add(path)

        if path.is_dir():
            matched_files |= get_statement_paths(path.iterdir())

    return matched_files


@click.command()
@click.version_option(package_name="monopoly-core")
@click.argument(
    "files",
    nargs=-1,
    type=click.Path(exists=True, allow_dash=True, resolve_path=True, path_type=Path),
)
@click.option(
    "-o",
    "--output",
    "output_directory",
    type=click.Path(exists=True, allow_dash=True, resolve_path=True, path_type=Path),
    help="Specify output folder.",
)
@click.option(
    "--preserve-filename",
    is_flag=True,
    help="Keep the input filename (with .csv extension) instead of generating a new one.",
)
@click.option(
    "-p",
    "--pprint",
    is_flag=True,
    help="Print the processed statement(s).",
)
@click.option(
    "-s",
    "--single-process",
    is_flag=True,
    help=("Runs `monopoly` in single-threaded mode, even when processing multiple files. Useful for debugging."),
)
@click.option(
    "--safe/--nosafe",
    "safety_check",
    default=True,
    help=("Determines whether to run the safety check or not. Runs the safety check by default."),
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help=("Increases logging verbosity."),
)
@click.option(
    "--ocr",
    "use_ocr",
    is_flag=True,
    help=("Apply OCR to extract text from scanned documents."),
)
@click.pass_context
@setup_logs
def monopoly(ctx: click.Context, files: list[Path], **kwargs):
    """
    Monopoly converts your bank statements from PDF to CSV.

    A file or directory can be passed in via the FILES argument
    """
    if files:
        matched_files = get_statement_paths(files)

        if matched_files:
            run(matched_files, RunConfig(**kwargs))

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
    message = "Monopoly converts your bank statements from PDF to CSV"
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
            "monopoly . --ocr",
            "applies OCR to extract text from scanned documents",
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
