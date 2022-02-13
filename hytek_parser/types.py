import csv
from os import PathLike
from typing import TYPE_CHECKING, Union

StrOrBytesPath = Union[
    str, bytes, PathLike[str], PathLike[bytes]
]  # from python/typeshed

# Wow Mypy is really annoying with these typings
if TYPE_CHECKING:
    DictReader = csv.DictReader[str]
else:
    DictReader = csv.DictReader
