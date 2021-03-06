import itertools
from pathlib import Path
from typing import Dict
from typing import Iterable
from typing import List
from typing import Mapping
from typing import Sequence
from typing import Set

import polib


class PoFileStats:
    """Class for each `.po` file containing all the necessary information about its progress
    """

    def __init__(self, path: Path):
        """Initializes the class with all the correct information
        """
        self.path: Path = path
        self.filename: str = path.name
        self.pofile: polib.POFile = polib.pofile(self.path)
        self.directory: str = self.path.parent.name

        self.obsolete_entries: Sequence[polib.POEntry] = self.pofile.obsolete_entries()
        self.obsolete_nb: int = len(self.pofile.obsolete_entries())

        self.fuzzy_entries: List[polib.POEntry] = [
            entry for entry in self.pofile if entry.fuzzy and not entry.obsolete
        ]
        self.fuzzy_nb: int = len(self.fuzzy_entries)

        self.translated_entries: Sequence[
            polib.POEntry
        ] = self.pofile.translated_entries()
        self.translated_nb: int = len(self.translated_entries)

        self.untranslated_entries: Sequence[
            polib.POEntry
        ] = self.pofile.untranslated_entries()
        self.untranslated_nb: int = len(self.untranslated_entries)

        self.percent_translated: int = self.pofile.percent_translated()
        self.po_file_size = len(self.pofile) - self.obsolete_nb
        self.filename_dir: str = self.directory + "/" + self.filename

    def __str__(self) -> str:
        return (
            f"Filename: {self.filename}\n"
            f"Fuzzy Entries: {self.fuzzy_entries}\n"
            f"Percent Translated: {self.percent_translated}\n"
            f"Translated Entries: {self.translated_entries}\n"
            f"Untranslated Entries: {self.untranslated_entries}"
        )

    def __lt__(self, other: "PoFileStats") -> bool:
        """When two PoFiles are compared, their filenames are compared.
        """
        return self.filename < other.filename


def is_within(file: Path, excluded: Path) -> bool:
    """Check if `file` is `excluded` or within `excluded`'s tree.
    """
    return excluded in file.parents or file == excluded


def get_po_stats_from_repo(
    repo_path: Path, exclude: Iterable[Path]
) -> Mapping[str, Sequence[PoFileStats]]:
    """Gets all the po files recursively from 'repo_path', excluding those in
    'exclude'. Return a dict with all directories and PoFile instances of
    `.po` files in those directories.
    """

    # Get all the files matching `**/*.po`
    # not being in the exclusion list or in
    # any (sub)folder from the exclusion list
    all_po_files: Sequence[Path] = [
        file
        for file in repo_path.rglob("*.po")
        if not any(is_within(file, excluded) for excluded in exclude)
    ]

    # Group files by directory
    po_files_per_directory: Mapping[str, Set[Path]] = {
        name: set(files)
        # We assume the output of rglob to be sorted,
        # so each 'name' is unique within groupby
        for name, files in itertools.groupby(
            all_po_files, key=lambda path: path.parent.name
        )
    }

    # Turn paths into stat objects
    po_stats_per_directory: Dict[str, Sequence[PoFileStats]] = {
        directory: [PoFileStats(po_file) for po_file in po_files]
        for directory, po_files in po_files_per_directory.items()
    }

    return po_stats_per_directory
