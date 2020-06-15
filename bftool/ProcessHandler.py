import bftool
import threading
import types
import multiprocessing
import queue


class ProcessHandler(multiprocessing.Process):
    def __init__(self, function_: types.FunctionType, wordlist: tuple,
                 max_threads: int, mode: int, print_queue):
        multiprocessing.Process.__init__(self)
        self.__function = function_
        self.__wordlist = wordlist
        self.__active_threads = 0
        self.__max_threads = max_threads
        self.__mode = mode
        self.__threads_queue = queue.Queue()
        self.__print_queue = print_queue

    def _wordlist_block_mode(self):
        for wordlist in bftool.wordlist_divider(self.__wordlist, self.__max_threads):
            if self.__active_threads > self.__max_threads:
                self.__threads_queue.get().join()
                self.__active_threads -= 1
            wordlist_block_thread = bftool.ThreadHandler(wordlist, self.__function, self.__print_queue)
            self.__threads_queue.put(wordlist_block_thread)
            wordlist_block_thread.start()
            self.__active_threads += 1

    def __arguments_mode_function(self, *args, **kargs):
        result = self.__function(*args, **kargs)
        if result:
            self.__print_queue.put(result)

    def _arguments_block_mode(self):
        for arguments in self.__wordlist:
            if self.__active_threads > self.__max_threads:
                self.__threads_queue.get().join()
                self.__active_threads -= 1
            arguments_thread = threading.Thread(target=self.__arguments_mode_function, args=arguments)
            self.__threads_queue.put(arguments_thread)
            arguments_thread.start()
            self.__active_threads += 1

    def run(self):
        if self.__mode == bftool.Modes.WORDLIST_BLOCK:
            self._wordlist_block_mode()
        elif self.__mode == bftool.Modes.BASIC_MODE:
            self._arguments_block_mode()
        exit(-1)
