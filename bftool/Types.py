import typing


class SpecialGenerator(object):
    def __init__(self, generator_function, *args):
        self.function = generator_function
        self.arguments = args

    def __call__(self, *args, **kwargs):
        return self.function(*self.arguments)


class IterableWordlists(typing.Dict):
    argument: int or str
    wordlist_iterable: typing.Iterable


class BruteforceWordlists(typing.Dict):
    argument: int or str
    rule: SpecialGenerator


class FilesWordlists(typing.Dict):
    argument: int or str
    file_path: SpecialGenerator


class ExpandableTuple(tuple):
    def __str__(self):
        return f"ExpandableTuple({', '.join(str(value) for value in self)})"

    def __repr__(self):
        return f"ExpandableTuple({', '.join(str(value) for value in self)})"
