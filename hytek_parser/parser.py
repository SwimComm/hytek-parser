from os import PathLike
from typing import Union

from loguru import logger

from .line_parsers import LINE_PARSERS
from .schemas import ParsedHytekFile

StrOrBytesPath = Union[
    str, bytes, PathLike[str], PathLike[bytes]
]  # from python/typeshed


def parse_hy3(
    file: StrOrBytesPath, validate_checksums: bool = False
) -> ParsedHytekFile:
    """Parse a Hytek MeetManager .hy3 file.

    Args:
        file (StrOrBytesPath): A path to the file to parse.
        validate_checksums (bool, optional): Validate line checksums. Defaults to False.

    Returns:
        ParsedHY3: The parsed file.
    """
    logger.info(f"Parsing Hytek meet entries file {file!r}.")

    if validate_checksums:
        raise NotImplementedError("Validating checksums has not been implemented yet.")

    # Read file
    with open(file) as f:
        lines = [line.strip() for line in f]

    # Make sure this is the right kind of file
    if lines[0][0:2] != "A1":
        raise ValueError("Not a Hytek file!")

    # Add terminator to file
    if lines[-1][0:2] != "Z0":
        lines.append("Z0")

    # Start parsing
    parsed_file = ParsedHytekFile()

    for line in lines:
        code = line[0:2]
        logger.debug(code)
        logger.debug(parsed_file)

        try:
            LINE_PARSERS[code](line, parsed_file)
        except KeyError:
            logger.warning(f"Invalid line code: {code}")
            continue
        except ValueError:
            logger.exception("Error parsing line!")
            continue

    return parsed_file
