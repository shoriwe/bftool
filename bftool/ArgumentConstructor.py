import collections
import inspect
import typing
import string
import bftool
import bftool.Types
import bftool.Modes
import bftool.WordlistHandler


# This class prepare all the arguments that the MainHandler is going to use
class Arguments(object):
    """Class that handles all the configuration of the the arguments that are going to be passed
    to `bftool.MainHandler.MainHandler`"""
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
        """
            - function_: The function object to be used
            - script_path: The script path with the source code of the wanted function (Incompatible with `function_`)
            - function_name: The function to be imported (Incompatible with `function_`)
            - wordlists_iterables: Dictionary with the iterables that are going to be passed to the arguments, please
            - notice that if you want to pass a generator object you may construct it with bftool.Types.SpecialGenerator
            - wordlists_pure_bruteforce_rules: Dict with the bruteforce rules that are going to be passed to the
            function
            - wordlists_files: Dict with the wordlists paths that are going to be passed to the function
            - maximum_number_of_concurrent_processes: maximum number of concurrent processes
            - maximum_number_of_process_threads: maximum number of concurrent threads per process
            - fuzzing_mode: the fuzzing mode
        """
        # - Function Setup
        # When the users bftool as a module and not a script he can provide the raw function object
        if isinstance(function_, collections.abc.Callable):
            self.function = function_
        # When the user specify that the function is going to be extracted of another python file
        elif isinstance(script_path, str) and isinstance(function_name, str):
            self.function = bftool.import_function_from_script(script_path, function_name)
        else:
            raise ValueError("No function provided")
        function_args_spec = inspect.getfullargspec(self.function)

        # - Wordlist Setup
        # This is the argument that will replace replace WordlistHandler.wordlist
        wordlists_for_handler: (int, [bftool.Types.SpecialGenerator, typing.Iterable[None], None])
        wordlists_for_handler = [None] * len(function_args_spec.args)

        # If the user provide raw iterables like list, sets, tuples, dicts...
        # To handle generators please check bftool.Types.SpecialGenerator
        if wordlists_iterables:
            for key, value in wordlists_iterables.items():
                if key[0] in string.digits:
                    wordlists_for_handler[int(key)] = value
                elif isinstance(key, str):
                    wordlists_for_handler[function_args_spec.args.index(key)] = value
                else:
                    raise KeyError(f"Can't index in the function arguments key {key} of type {type(key)}")

        # If the user provides wordlist generation rules
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

        # If the user provide a file as a wordlist (it always read each line as an argument)
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
