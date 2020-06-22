import bftool
import bftool.Types


class WordlistHandler(object):
    def __init__(self):
        self.wordlists = []
        self.__master_wordlist = None

    def __iter__(self):
        return self.__master_wordlist

    def __next__(self):
        return next(self.__master_wordlist)

    def wordlist_from_files(self, *args):
        for wordlist_path in args:
            self.wordlists.append(bftool.Types.SpecialGenerator(bftool.read_file_lines, wordlist_path))

    def pure_bruteforce_setup(self, *args):
        for rule in args:
            self.wordlists.append(bftool.Types.SpecialGenerator(bftool.pure_bruteforce_rule, rule))

    def wordlist_from_iterable(self, *args):
        self.wordlists.extend(args)

    def setup(self):
        # self.__master_wordlist = bftool.custom_product(*self.__wordlists)  # At the end this never work
        self.__master_wordlist = bftool.custom_product(self.wordlists)

    def get(self):
        try:
            return next(self.__master_wordlist)
        except StopIteration:
            return None
