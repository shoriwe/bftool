from .Types import SpecialGenerator


def _read_file_lines(file_path: str):
    """Function that iterates over a file lines, eat less memory than reading it at once

    Arguments:
        - file_path: Path to the wordlist file

    Returns:
        - Yield each line of the file
    """
    file_object = open(file_path, errors="ignore")
    for line in file_object:
        yield line[:-1] if line[-1] == "\n" else line
    file_object.close()


def read_file_lines(file_path: str) -> SpecialGenerator:
    return SpecialGenerator(_read_file_lines, file_path)
