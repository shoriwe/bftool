import types
import itertools
import importlib
import os
import argparse
import copy
import multiprocessing
import bftool.Types
import bftool.Modes
import bftool.ArgumentConstructor
import bftool.WordlistHandler


def get_wordlist_from_path(wordlist_path: str):
    with open(wordlist_path, "r", errors="ignore") as file_obj:
        content = map(lambda word: word[:-1], file_obj.readlines())
        file_obj.close()
    return content


# Get the wordlists from the files supplied
def get_wordlists_from_paths(wordlists_paths: tuple) -> iter:
    for wordlist_path in wordlists_paths:
        yield get_wordlist_from_path(wordlist_path)


# Import a python module from it's filesystem path
def import_module_from_path(main_py_path: str) -> types.ModuleType:
    if not os.path.exists(main_py_path):
        raise FileExistsError("Looks like file not exists")
    if not os.path.isfile(main_py_path):
        raise TypeError("Looks like path supplied is not a file")
    module_name = main_py_path.replace("\\", "/").split("/")[-1].split(".")[0]
    return importlib.import_module(module_name, main_py_path)


def import_function_from_script(script_path: str, function_name: str):
    module = import_module_from_path(script_path)
    return getattr(module, function_name)


# Split a wordlist in smaller sub wordlists
def wordlist_divider(wordlist: tuple, step: int) -> tuple:
    length = len(wordlist)
    if step > length:
        raise IndexError("The division step can't be higher than the wordlist length")
    wordlist_step = int(length / step)
    for number in range(length):
        if wordlist_block := wordlist[number*wordlist_step:(number+1)*wordlist_step]:
            yield wordlist_block
        else:
            break


# Function to merge wordlist
def merge_wordlists(*args):
    return tuple(itertools.product(*args))


# chars, minlength, maxlength
def pure_bruteforce_rule(rule: str):
    rule = dict(value.split("=") for value in rule.split(","))
    rule["minlength"] = int(rule["minlength"])
    rule["maxlength"] = int(rule["maxlength"])
    for length in range(rule["minlength"], rule["maxlength"]+1):
        for word in itertools.product(*(rule["chars"] for number in range(length))):
            yield "".join(word)


def read_file_lines(file_path: str):
    file_object = open(file_path, errors="ignore")
    for line in file_object:
        yield line[:-1]
    file_object.close()


# By StackOverFlow user @jfs
# https://stackoverflow.com/questions/533905/get-the-cartesian-product-of-a-series-of-lists
def custom_product(*args):
    copied = (copy.copy(iterable) for iterable in args)
    if not args:
        return iter(((),))  # yield tuple()
    return (items + (item,)
            for items in custom_product(*copied[:-1]) for item in args[-1])


def arguments_queue_handler(arguments_queue: multiprocessing.Queue,
                            wordlist_handler: bftool.WordlistHandler.WordlistHandler):
    for argument in wordlist_handler:
        arguments_queue.put(argument)
    exit(0)


# Default argument capture for the main function
def get_arguments() -> bftool.ArgumentConstructor.Arguments:
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
    argument_parser.add_argument("script_path", help="Path to the python script to the function to use")
    argument_parser.add_argument("function_name", help="Name of the function to use")
    parsed_arguments = argument_parser.parse_args()
    if parsed_arguments.mode == "wordlist":
        parsed_arguments.mode = bftool.Modes.WORDLIST_BLOCK
    elif parsed_arguments == "arguments":
        parsed_arguments.mode = bftool.Modes.ARGUMENTS_MODE
    arguments = bftool.ArgumentConstructor.Arguments(script_path=parsed_arguments.script_path,
                                                     function_name=parsed_arguments.function_name,
                                                     wordlists_files=bftool.Types.FilesWordlists(wordlist.split(":")
                                                                          for wordlist in parsed_arguments.wordlist),
                                                     wordlists_pure_bruteforce_rules=bftool.Types.BruteforceWordlists(
                                                         wordlist.split(":")
                                                         for wordlist in parsed_arguments.bruteforce),
                                                     maximum_number_of_concurrent_processes=parsed_arguments.max_processes,
                                                     maximum_number_of_process_threads=parsed_arguments.max_threads,
                                                     fuzzing_mode=parsed_arguments.mode,
                                                     )
    return arguments
