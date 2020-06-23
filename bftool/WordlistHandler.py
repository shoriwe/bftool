import bftool
import bftool.Types


class WordlistHandler(object):
    """This class provide a high level understanding on how the arguments are prepared and then read by the
    `MainHandler`"""
    def __init__(self):
        self.wordlists = []
        self.__master_wordlist = None

    def __iter__(self):
        return self.__master_wordlist

    def __next__(self):
        return next(self.__master_wordlist)

    def wordlist_from_files(self, *args):
        """Prepare all the wordlists from a list of file paths, understand that this function is not smart enough to
        organize them by index or by argument name like `bftool.ArgumentConstructor.Arguments` does"""
        for wordlist_path in args:
            self.wordlists.append(bftool.Types.SpecialGenerator(bftool.read_file_lines, wordlist_path))

    def pure_bruteforce_setup(self, *args):
        """Prepare all the wordlists from a list of bruteforce rules, understand that this function is not smart enough
        to organize them by index or by argument name like `bftool.ArgumentConstructor.Arguments` does"""
        for rule in args:
            self.wordlists.append(bftool.Types.SpecialGenerator(bftool.pure_bruteforce_rule, rule))

    def wordlist_from_iterable(self, *args):
        """Prepare all the wordlists from a list of iterables, understand that this function is not smart enough to
        organize them by index or by argument name like `bftool.ArgumentConstructor.Arguments` does"""
        self.wordlists.extend(args)

    def setup(self):
        """This function prepare the master wordlist to be  used by an iterator"""
        # self.__master_wordlist = bftool.custom_product(*self.__wordlists)  # At the end this never work
        self.__master_wordlist = bftool.custom_product(self.wordlists)

    def get(self):
        """A friendly way to handle the iteration of the master wordlist from a while loop"""
        try:
            return next(self.__master_wordlist)
        except StopIteration:
            return None
