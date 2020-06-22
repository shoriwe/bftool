import collections
import inspect
import typing
import string
import bftool
import bftool.Types
import bftool.Modes
import bftool.WordlistHandler


class Arguments(object):
    def __init__(self,
                 function_: collections.abc.Callable = None,
                 script_path: str = None,
                 function_name: str = None,
                 wordlists_iterables: bftool.Types.IterableWordlists = None,
                 wordlists_pure_bruteforce_rules: bftool.Types.BruteforceWordlists = None,
                 wordlists_files: bftool.Types.FilesWordlists = None,
                 maximum_number_of_concurrent_processes: int = 1,
                 maximum_number_of_process_threads: int = 1,
                 fuzzing_mode: bftool.Modes = bftool.Modes.ARGUMENTS_MODE,
                 ):
        if isinstance(function_, collections.abc.Callable):
            self.function = function_
        elif isinstance(script_path, str) and isinstance(function_name, str):
            self.function = bftool.import_function_from_script(script_path, function_name)
        else:
            raise ValueError("No function provided")
        function_args_spec = inspect.getfullargspec(self.function)

        wordlists_for_handler: (int, [bftool.Types.SpecialGenerator, typing.Iterable[None], None])
        wordlists_for_handler = [None] * len(function_args_spec.args)
        if wordlists_iterables:
            for key, value in wordlists_iterables.items():
                if key[0] in string.digits:
                    wordlists_for_handler[int(key)] = value
                elif isinstance(key, str):
                    wordlists_for_handler[function_args_spec.args.index(key)] = value
                else:
                    raise KeyError(f"Can't index in the function arguments key {key} of type {type(key)}")
        if wordlists_pure_bruteforce_rules:
            for key, value in wordlists_pure_bruteforce_rules.items():
                if key[0] in string.digits:
                    # noinspection PyTypeChecker
                    wordlists_for_handler[int(key)] = bftool.Types.SpecialGenerator(bftool.pure_bruteforce_rule, value)
                elif isinstance(key, str):
                    # noinspection PyTypeChecker
                    wordlists_for_handler[function_args_spec.args.index(key)] =\
                        bftool.Types.SpecialGenerator(bftool.pure_bruteforce_rule, value)
                else:
                    raise KeyError(f"Can't index in the function arguments key {key} of type {type(key)}")

        if wordlists_files:
            for key, value in wordlists_files.items():
                if key[0] in string.digits:
                    # noinspection PyTypeChecker
                    wordlists_for_handler[int(key)] =\
                        bftool.Types.SpecialGenerator(bftool.get_wordlist_from_path, value)
                elif isinstance(key, str):
                    # noinspection PyTypeChecker
                    wordlists_for_handler[function_args_spec.args.index(key)] =\
                        bftool.Types.SpecialGenerator(bftool.get_wordlist_from_path, value)
                else:
                    raise KeyError(f"Can't index in the function arguments key {key} of type {type(key)}")

        if not wordlists_for_handler:
            raise ValueError("No wordlist input provided")

        if any(value is None for value in wordlists_for_handler):
            raise IndexError(f"Invalid number of wordlists provided ({len(wordlists_for_handler)})"
                             f"for a function of {len(function_args_spec.args)} arguments")

        self.wordlist_handler = bftool.WordlistHandler.WordlistHandler()
        self.wordlist_handler.wordlists = wordlists_for_handler
        self.wordlist_handler.setup()

        self.maximum_number_of_concurrent_processes = maximum_number_of_concurrent_processes
        self.maximum_number_of_process_threads = maximum_number_of_process_threads
        self.fuzzing_mode = fuzzing_mode
