from __future__ import annotations

import re
from pathlib import Path
from typing import Callable, Iterator, Optional


class DisplayablePath:
    display_filename_prefix_middle = "├──"
    display_filename_prefix_last = "└──"
    display_parent_prefix_middle = "    "
    display_parent_prefix_last = "│   "

    def __init__(self, path: Path, parent_path: Optional[DisplayablePath], *, is_last: bool) -> None:
        self.path = Path(str(path))
        self.parent = parent_path
        self.is_last = is_last
        if self.parent:
            self.depth: int = self.parent.depth + 1
        else:
            self.depth = 0

    @property
    def display_name(self) -> str:
        if self.path.is_dir():
            return self.path.name + "/"
        return self.path.name

    @classmethod
    def make_tree(
        cls,
        root: Path,
        parent: Optional[DisplayablePath] = None,
        criteria: Optional[Callable[[Path], bool]] = None,
        *,
        is_last: bool = False,
    ) -> Iterator[DisplayablePath]:
        root = Path(str(root))
        criteria = criteria or cls._default_criteria

        displayable_root = cls(root, parent, is_last=is_last)
        yield displayable_root

        children = sorted([path for path in root.iterdir() if criteria(path)], key=lambda s: str(s).lower())
        count = 1
        for path in children:
            is_last = count == len(children)
            if path.is_dir():
                yield from cls.make_tree(path, parent=displayable_root, is_last=is_last, criteria=criteria)
            else:
                yield cls(path, displayable_root, is_last=is_last)
            count += 1

    @classmethod
    def _default_criteria(cls, _: Path) -> bool:
        return True

    def displayable(self) -> str:
        if self.parent is None:
            return self.display_name

        _filename_prefix = self.display_filename_prefix_last if self.is_last else self.display_filename_prefix_middle

        parts = [f"{_filename_prefix!s} {self.display_name!s}"]

        parent = self.parent
        while parent and parent.parent is not None:
            parts.append(self.display_parent_prefix_middle if parent.is_last else self.display_parent_prefix_last)
            parent = parent.parent

        return "".join(reversed(parts))


def print_tree(path: str) -> None:
    paths = DisplayablePath.make_tree(Path(path))
    for path_ in paths:
        print(path_.displayable())  # noqa: T201


def pluralize(word: str) -> str:
    if re.search("[sxz]$", word) or re.search("[^aeioudgkprt]h$", word):
        # Make it plural by adding es in end
        return re.sub("$", "es", word)
    # Check if word is ending with ay,ey,iy,oy,uy
    if re.search("[aeiou]y$", word):
        # Make it plural by removing y from end adding ies to end
        return re.sub("y$", "ies", word)
    # In all the other cases

    # Make the plural of word by adding s in end
    return word + "s"
