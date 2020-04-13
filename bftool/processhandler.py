import bftool
import threading
import types
import multiprocessing


class ProcessHandler(multiprocessing.Process):
    def __init__(self, function_: types.FunctionType, wordlist: tuple, active_threads: multiprocessing.Value,
                 active_processes: multiprocessing.Value, max_threads: int, mode: int):
        multiprocessing.Process.__init__(self)
        self.__function = function_
        self.__wordlist = wordlist
        self.__active_threads = active_threads
        self.__active_processes = active_processes
        self.__max_threads = max_threads
        self.__mode = mode

    def _wordlist_block_mode(self):
        for wordlist in bftool.wordlist_divider(self.__wordlist, self.__max_threads):
            while self.__active_threads.value > self.__max_threads:
                pass
            wordlist_block_thread = bftool.ThreadHandler(wordlist, self.__function, self.__active_threads)
            wordlist_block_thread.start()
            self.__active_threads.value += 1

    def __arguments_mode_function(self, *args, **kargs):
        self.__function(*args, **kargs)
        self.__active_threads.value -= 1

    def _arguments_block_mode(self):
        for arguments in self.__wordlist:
            while self.__active_threads.value > self.__max_threads:
                pass
            arguments_thread = threading.Thread(target=self.__arguments_mode_function, args=arguments)
            arguments_thread.start()
            self.__active_threads.value += 1

    def run(self):
        if self.__mode == bftool.Modes.WORDLIST_BLOCK:
            self._wordlist_block_mode()
        elif self.__mode == bftool.Modes.BASIC_MODE:
            self._arguments_block_mode()
        self.__active_processes.value -= 1
        exit(-1)
