import typing


# Low cost way to backup python generators for re-iterations
class SpecialGenerator(object):
    """Low cost way to backup python generators for re-iterations, so always use it when you whant to pass generators to
    `bftool.Arguments` so the arguments distribution generator (the master one) can understand how to revert it to it's
    original state"""
    def __init__(self, generator_function, *args):
        """
        Arguments:
            - generator_function: The function that creates the generator
            - args: the arguments to pass to that function
        """
        self.function = generator_function
        self.arguments = args

    def __call__(self, *args, **kwargs):
        return self.function(*self.arguments)


# Only a Fancy way to specify how those wordlist need to be prepared
class IterableWordlists(typing.Dict):
    """Structure of a Wordlist of iterables"""
    argument: int or str
    wordlist_iterable: typing.Iterable


class BruteforceWordlists(typing.Dict):
    """Structure of a wordlist of bruteforce rules"""
    argument: int or str
    rule: SpecialGenerator


class FilesWordlists(typing.Dict):
    """Structure of a wordlist of files"""
    argument: int or str
    file_path: SpecialGenerator


# Easies way to not expand arguments that are tuple
class ExpandableTuple(tuple):
    """Easies way to not expand arguments that are tuple, so if you are not going to work with the internal of the
    module please leave it"""
    def __str__(self):
        return f"ExpandableTuple({', '.join(str(value) for value in self)})"

    def __repr__(self):
        return f"ExpandableTuple({', '.join(str(value) for value in self)})"
