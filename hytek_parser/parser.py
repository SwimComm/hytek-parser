from os import PathLike
from typing import Any, Union

from loguru import logger

from .line_parsers.hy3 import LINE_PARSERS
from .schemas import ParsedHytekFile

StrOrBytesPath = Union[
    str, bytes, PathLike[str], PathLike[bytes]
]  # from python/typeshed


def parse_hy3(
    file: StrOrBytesPath, validate_checksums: bool = False, default_country: str = "USA"
) -> ParsedHytekFile:
    """Parse a Hytek MeetManager .hy3 file.

    Args:
        file (StrOrBytesPath): A path to the file to parse.
        validate_checksums (bool, optional): Validate line checksums. Defaults to False.
        default_country (str, optional): Default country for meet. Defaults to "USA".

    Returns:
        ParsedHytekFile: The parsed file.
    """
    logger.info(f"Parsing Hytek meet entries file {file!r}.")

    # TODO: Implement checksum validation
    if validate_checksums:
        logger.warning("Checksum validation not implemented, ignoring.")
        validate_checksums = False

    # Set options dict
    opts: dict[str, Any] = {
        "validate_checksums": validate_checksums,
        "default_country": default_country,
    }

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

    warnings = 0
    errors = 0
    for line in lines:
        code = line[0:2]
        logger.debug(code)

        if code == "Z0":
            # End of file
            break

        try:
            line_parser = LINE_PARSERS.get(code)

            if line_parser is None:
                logger.warning(f"Invalid line code: {code}")
                warnings += 1
                continue

            parsed_file = line_parser(line, parsed_file, opts)
        except Exception:
            logger.exception("Error parsing line!")
            errors += 1
            continue

    logger.success(f"Parse completed with {warnings} warning(s) and {errors} error(s).")
    return parsed_file
