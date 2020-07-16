import collections
import inspect
import string

from .Modes import ARGUMENTS_MODE
from .ImportCode import import_function_from_script
from .CartesianProduct import combine_wordlists
from .BruteforceWordlist import pure_bruteforce_wordlist
from .WordlistFromFile import read_file_lines


__all__ = ["Arguments"]


# This class prepare all the arguments that the MainHandler is going to use
class Arguments(object):
    """Class that handles all the configuration of the the arguments that are going to be passed
    to `bftool.MainHandler.MainHandler`"""

    def __init__(self,
                 function_: collections.abc.Callable = None,
                 success_function: collections.abc.Callable = print,
                 script_path: str = None,
                 function_name: str = None,
                 iterables_wordlists: dict = None,
                 bruteforce_rules_wordlists: dict = None,
                 files_wordlists: dict = None,
                 maximum_number_of_concurrent_processes: int = 1,
                 maximum_number_of_process_threads: int = 1,
                 fuzzing_mode=ARGUMENTS_MODE,
                 ):
        """
            - success_function: The function to use to pass the results of the executed function
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
        self._load_success_function(success_function)

        self._load_function(function_, script_path, function_name)

        # - Wordlist Setup
        # This is the argument that will replace replace WordlistHandler.wordlist
        self.__wordlists = [None] * len(self.__function_args_spec.args)

        self._load_words_from_iterables(iterables_wordlists)
        self._load_words_from_bruteforce_rules(bruteforce_rules_wordlists)
        self._load_words_from_files(files_wordlists)

        self.master_wordlist = combine_wordlists(self.__wordlists)

        self.maximum_number_of_concurrent_processes = maximum_number_of_concurrent_processes
        self.maximum_number_of_process_threads = maximum_number_of_process_threads
        self.fuzzing_mode = fuzzing_mode

    def _load_success_function(self, success_function: collections.abc.Callable):
        if callable(success_function):
            self.success_function = success_function
        else:
            raise TypeError("Success function must be callable")

    def _load_function(self,
                       function_: collections.abc.Callable = None,
                       script_path: str = None,
                       function_name: str = None):
        # - Function Setup
        # When the users bftool as a module and not a script he can provide the raw function object
        if isinstance(function_, collections.abc.Callable):
            self.function = function_
        # When the user specify that the function is going to be extracted of another python file
        elif isinstance(script_path, str) and isinstance(function_name, str):
            self.function = import_function_from_script(script_path, function_name)
        else:
            raise ValueError("No function provided")
        self.__function_args_spec = inspect.getfullargspec(self.function)

    def _load_words_from_iterables(self, iterables_wordlists: dict):
        # If the user provide raw iterables like list, sets, tuples, dicts...
        # To handle generators please check bftool.Types.SpecialGenerator
        if iterables_wordlists:
            for key, value in iterables_wordlists.items():
                if isinstance(key, int):
                    self.__wordlists[key] = value
                elif isinstance(key, str):
                    if key[0] in string.digits:
                        self.__wordlists[int(key)] = value
                    else:
                        self.__wordlists[self.__function_args_spec.args.index(key)] = value
                else:
                    raise KeyError(f"Can't index in the function arguments key {key} of type {type(key)}")

    def _load_words_from_bruteforce_rules(self, bruteforce_rules_wordlists: dict):
        # If the user provides wordlist generation rules
        if bruteforce_rules_wordlists:
            for key, value in bruteforce_rules_wordlists.items():
                if isinstance(key, int):
                    self.__wordlists[key] = pure_bruteforce_wordlist(value)
                elif isinstance(key, str):
                    if key[0] in string.digits:
                        self.__wordlists[int(key)] = pure_bruteforce_wordlist(value)
                    else:
                        self.__wordlists[self.__function_args_spec.args.index(key)] = pure_bruteforce_wordlist(value)
                else:
                    raise KeyError(f"Can't index in the function arguments key {key} of type {type(key)}")

    def _load_words_from_files(self, files_wordlists: dict):
        # If the user provide a file as a wordlist (it always read each line as an argument)
        if files_wordlists:
            for key, value in files_wordlists.items():
                if isinstance(key, int):
                    self.__wordlists[key] = read_file_lines(value)
                elif isinstance(key, str):
                    if key[0] in string.digits:
                        self.__wordlists[int(key)] = read_file_lines(value)
                    else:
                        self.__wordlists[self.__function_args_spec.args.index(key)] = read_file_lines(value)
                else:
                    raise KeyError(f"Can't index in the function arguments key {key} of type {type(key)}")

    def is_valid(self):
        """
        This functions checks that the prepared arguments are valid
        :return:
        """
        if not self.__wordlists:
            raise ValueError("No wordlist input provided")

        if any(value is None for value in self.__wordlists):
            raise IndexError(f"Invalid number of wordlists provided ({len(self.__wordlists)})"
                             f"for a function of {len(self.__function_args_spec.args)} arguments")
        return True
