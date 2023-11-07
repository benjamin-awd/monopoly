from pathlib import Path
from typing import Collection, Iterable

import click

from monopoly.banks import auto_detect_bank


def run(files: Collection[Path]):
    for file in files:
        bank = auto_detect_bank(file)
        statement = bank.extract()
        transformed_df = bank.transform(statement)
        bank.load(transformed_df, statement)


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
def monopoly(files: list[Path]):
    """
    Monopoly helps convert your bank statements from PDF to CSV.

    A file or directory can be passed in via the FILES argument
    """
    if files:
        matched_files = get_statement_paths(files)
        run(matched_files)

    else:
        print("No command received")
