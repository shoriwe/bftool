import types
import importlib
import os
import argparse
import multiprocessing
import bftool.Types
import bftool.Modes
import bftool.ArgumentConstructor
import bftool.WordlistHandler


def get_wordlist_from_path(wordlist_path: str):
    """Function to read all lines of a file"""
    with open(wordlist_path, "r", errors="ignore") as file_obj:
        content = map(lambda word: word[:-1] if word[-1] == "\n" else word, file_obj.readlines())
        file_obj.close()
    return content


# Get the wordlists from the files supplied
def get_wordlists_from_paths(wordlists_paths: tuple) -> iter:
    """Function to provide a generator with all the content of the input files"""
    for wordlist_path in wordlists_paths:
        yield get_wordlist_from_path(wordlist_path)


# Import a python module from it's filesystem path
def import_module_from_path(main_py_path: str) -> types.ModuleType:
    """Import a python module from it's FileSystem path"""
    if not os.path.exists(main_py_path):
        raise FileExistsError("Looks like file not exists")
    if not os.path.isfile(main_py_path):
        raise TypeError("Looks like path supplied is not a file")
    module_name = main_py_path.replace("\\", "/").split("/")[-1].split(".")[0]
    return importlib.import_module(module_name, main_py_path)


def import_function_from_script(script_path: str, function_name: str):
    """Function to extract the a python function from a module"""
    module = import_module_from_path(script_path)
    return getattr(module, function_name)


# Split a wordlist in smaller sub wordlists
def wordlist_divider(wordlist: tuple, step: int) -> tuple:
    """Function to divide a wordlist of `N` size in small wordlists of sizes `step`"""
    length = len(wordlist)
    if step > length:
        raise IndexError("The division step can't be higher than the wordlist length")
    wordlist_step = int(length / step)
    for number in range(length):
        if wordlist_block := wordlist[number * wordlist_step:(number + 1) * wordlist_step]:
            yield wordlist_block
        else:
            break


# chars, minlength, maxlength
def pure_bruteforce_rule(rule: str):
    """Function that creates a virtual wordlist based on rules.
    Necessary rules:
        - `chars=string` : All the chars that are going to be used during the cartesian product
        - `minlength=int` : Minimum length of generated words
        - `maxlength=` : maximum length of generated words"""
    # noinspection PyTypeChecker
    rule = dict(value.split("=") for value in rule.split(","))
    rule["minlength"] = int(rule["minlength"])
    rule["maxlength"] = int(rule["maxlength"])
    for length in range(rule["minlength"], rule["maxlength"] + 1):
        for word in cartesian_product(rule["chars"], length):
            yield "".join(word)


def read_file_lines(file_path: str):
    """Function that iterates over a file lines, eat less memory than reading it at once"""
    file_object = open(file_path, errors="ignore")
    for line in file_object:
        yield line[:-1]
    file_object.close()


def arguments_queue_handler(arguments_queue: multiprocessing.Queue,
                            wordlist_handler: bftool.WordlistHandler.WordlistHandler):
    """Fill the `arguments_queue` of the `MainHandler` with the arguments provided by `WordlistHandler`"""
    for argument in wordlist_handler:
        arguments_queue.put(argument)
    exit(0)


# Default argument capture for the main function
def get_arguments() -> bftool.ArgumentConstructor.Arguments:
    """Default function to prepare the arguments for the `MainHandler` during it's execution in a terminal"""
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("-mt", "--max-threads",
                                 help="Maximum number of threads per process (if mode is set to wordlist block, \
                                 this will be also the worlist division number)", default=1, type=int)
    argument_parser.add_argument("-mp", "--max-processes",
                                 help="Maximum number of process to have active at the same time",
                                 default=bftool.Modes.ARGUMENTS_MODE, type=int)
    argument_parser.add_argument("-w", "--wordlist", help="File wordlist to use"
                                                          " based on \"[ARGUMENT_INDEX, ARGUMENT_NAME]:file_path\"",
                                 action="append", default=[])
    argument_parser.add_argument("-b", "--bruteforce",
                                 help="Generate a virtual wordlist based on \
                                 rules \"[ARGUMENT_INDEX, ARGUMENT_NAME]:chars=...,minlength=...,maxlength=...\"",
                                 action="append", default=[])
    argument_parser.add_argument("-m", "--mode",
                                 help="Mode to use during the function execution (way to divide the threads)",
                                 choices=("wordlist", "arguments"), default="arguments")
    argument_parser.add_argument("script_path", help="Python script to import")
    argument_parser.add_argument("function_name", help="Name of the function implemented in the python script to use")
    parsed_arguments = argument_parser.parse_args()
    if parsed_arguments.mode == "wordlist":
        parsed_arguments.mode = bftool.Modes.WORDLIST_BLOCK
    elif parsed_arguments.mode == "arguments":
        parsed_arguments.mode = bftool.Modes.ARGUMENTS_MODE
    arguments = bftool.ArgumentConstructor.Arguments(script_path=parsed_arguments.script_path,
                                                     function_name=parsed_arguments.function_name,
                                                     wordlists_files=
                                                     bftool.Types.FilesWordlists(wordlist.split(":")
                                                                                 for wordlist in
                                                                                 parsed_arguments.wordlist),
                                                     wordlists_pure_bruteforce_rules=bftool.Types.BruteforceWordlists(
                                                         wordlist.split(":")
                                                         for wordlist in parsed_arguments.bruteforce),
                                                     maximum_number_of_concurrent_processes=
                                                     parsed_arguments.max_processes,
                                                     maximum_number_of_process_threads=parsed_arguments.max_threads,
                                                     fuzzing_mode=parsed_arguments.mode,
                                                     )
    return arguments


def cartesian_product(iterable_: iter, length: int, join=False):
    """Custom cartesian product that creates product on the fly"""
    try:
        iterable_ = tuple(set(iterable_))
    except TypeError:
        pass
    if length < 1:
        raise ValueError("Invalid length supplied")
    indexes = [0] * length
    chars_length = len(iterable_)
    while True:
        if not join:
            yield tuple(iterable_[index] for index in indexes)
        else:
            yield "".join(iterable_[index] for index in indexes)
        for index, index_value in enumerate(indexes):
            if indexes[index] < chars_length - 1:
                indexes[index] += 1
                break
            else:
                indexes[index] = 0
        if all(index == 0 for index in indexes):
            break


def expand_product(product: tuple) -> list:
    """This function expand in it's correct way, the arguments provided by custom product"""
    result = []
    for value in product:
        if isinstance(value, bftool.Types.ExpandableTuple):
            result += expand_product(value)
        elif isinstance(value, tuple):
            if len(value) == 1:  # If the tuple is just one argument
                result.append(value[0])
            else:
                result.append(value)
        else:
            result.append(value)
    return result


# Expected input
# [bftool.Types.SpecialGenerator, list, tuple, set, dict, ...] (list of iterables)
def custom_product(iterables_: list, master=True):
    """This function is intended to handle the cartesian product of all arguments"""
    number_of_iterables = len(iterables_)
    if isinstance(iterables_[0], bftool.Types.SpecialGenerator):
        cycle_iterable = iterables_[0]()
    else:
        cycle_iterable = iterables_[0]
    if number_of_iterables == 1:
        for value in cycle_iterable:
            yield value,
    elif number_of_iterables > 1:
        for value in cycle_iterable:
            for second_value in custom_product(iterables_[1:], False):
                second_value = bftool.Types.ExpandableTuple(second_value)
                if master:
                    # When is the master function (the one that the user called), normalize it's values
                    yield expand_product((value, second_value))
                else:
                    yield value, second_value
    else:
        raise IndexError("Invalid number of arguments")
