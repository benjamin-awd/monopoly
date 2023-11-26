from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Collection, Iterable, Optional

import click
from tqdm import tqdm

from monopoly.banks import auto_detect_bank


def process_statement(file: Path, output_directory: Optional[Path]):
    bank = auto_detect_bank(file)
    statement = bank.extract()
    transformed_df = bank.transform(statement)

    # saves processed statements to the same directory by default
    if not output_directory:
        output_directory = file.parent

    output_file = bank.load(transformed_df, statement, output_directory)
    return file.name, output_file.name


def run(input_files: Collection[Path], output_directory: Optional[Path] = None):
    with ProcessPoolExecutor() as executor:
        results = list(
            tqdm(
                executor.map(
                    process_statement,
                    input_files,
                    [output_directory] * len(input_files),
                ),
                total=len(input_files),
                desc="Processing statements",
                ncols=80,
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}",
            )
        )

    click.echo(click.style(f"{len(input_files)} statement(s) processed", bold=True))
    for raw_statement, processed_statement in sorted(results):
        click.echo(f"{raw_statement} -> {processed_statement}")


def get_statement_paths(files: Iterable[Path]) -> set[Path]:
    matched_files = set()
    for path in files:
        if path.is_file() and str(path).endswith(".pdf"):
            matched_files.add(path)

        if path.is_dir():
            matched_files |= get_statement_paths(path.iterdir())

    return matched_files


@click.command()
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
@click.pass_context
def monopoly(ctx: click.Context, files: list[Path], output: Path):
    """
    Monopoly helps convert your bank statements from PDF to CSV.

    A file or directory can be passed in via the FILES argument
    """
    if files:
        matched_files = get_statement_paths(files)

        if matched_files:
            run(matched_files, output)
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
            "process a specific statement in a directory",
        ),
        (
            "monopoly . --output <dir>",
            "saves all results to a specific directory",
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
