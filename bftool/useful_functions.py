import types
import itertools
import importlib
import os
import argparse


# Get the wordlists from the files supplied
def get_wordlists(wordlists_paths: tuple) -> iter:
    for wordlist_path in wordlists_paths:
        with open(wordlist_path, "r", errors="ignore") as file_obj:
            yield map(lambda word: word[:-1], file_obj.readlines())
            file_obj.close()


# Import a python module from it's filesystem path
def import_module_from_path(main_py_path: str) -> types.ModuleType:
    if not os.path.exists(main_py_path):
        raise FileExistsError("Looks like file not exists")
    if not os.path.isfile(main_py_path):
        raise TypeError("Looks like path supplied is not a file")
    module_name = main_py_path.replace("\\", "/").split("/")[-1].split(".")[0]
    return importlib.import_module(module_name, main_py_path)


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


# Default argument capture for the main function
def get_arguments():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("-mt", "--max-threads",
                                 help="Maximum number of threads per process (if mode is set to wordlist block, \
                                 this will be also the worlist division number)", default=1, type=int)
    argument_parser.add_argument("-mp", "--max-processes",
                                 help="Maximum number of process to have active at the same time",
                                 default=1, type=int)
    argument_parser.add_argument("-w", "--wordlist", help="Wordlist to use (can be used more than once)",
                                 action="append", required=True)
    argument_parser.add_argument("-m", "--mode",
                                 help="Mode to use during the function execution (way to divide the threads)",
                                 choices=("wordlist", "arguments"), default="arguments")
    argument_parser.add_argument("module_path", help="Path to the python module to the function to use")
    argument_parser.add_argument("function_name", help="Name of the function to use")
    return argument_parser.parse_args()
