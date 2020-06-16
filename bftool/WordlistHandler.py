import itertools
import bftool


class WordlistHandler(object):
    def __init__(self):
        self.__wordlists = []
        self.__master_wordlist = None

    def __iter__(self):
        return self.__master_wordlist

    def __next__(self):
        return next(self.__master_wordlist)

    def wordlist_from_files(self, *args):
        for wordlist_path in args:
            self.__wordlists.append(bftool.read_file_lines(wordlist_path))

    def pure_bruteforce_setup(self, *args):
        for rule in args:
            self.__wordlists.append(bftool.pure_bruteforce_rule(rule))

    def setup(self):
        # self.__master_wordlist = bftool.custom_product(*self.__wordlists)
        self.__master_wordlist = itertools.product(*self.__wordlists)

    def get(self):
        try:
            return next(self.__master_wordlist)
        except StopIteration:
            return None
