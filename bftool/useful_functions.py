import types
import itertools
import importlib
import os


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
