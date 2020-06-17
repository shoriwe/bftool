import typing


class IterableWordlists(typing.Dict):
    argument: int or str
    wordlist_iterable: typing.Iterable


class BruteforceWordlists(typing.Dict):
    argument: int or str
    rule: str


class FilesWordlists(typing.Dict):
    argument: int or str
    file_path: str
