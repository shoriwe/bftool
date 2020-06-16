import threading
import types
import multiprocessing
import queue
import bftool
import bftool.WordlistHandler
import bftool.ThreadHandler


class ProcessHandler(multiprocessing.Process):
    def __init__(self, process_id: int, function_: types.FunctionType, wordlist: bftool.WordlistHandler.WordlistHandler,
                 max_threads: int, mode: int, print_queue):
        multiprocessing.Process.__init__(self)
        self.__process_id = process_id
        self.__function = function_
        self.__wordlist_handler = wordlist
        self.__active_threads = 0
        self.__max_threads = max_threads
        self.__mode = mode
        self.__threads_queue = queue.Queue()
        self.__print_queue = print_queue

    def _wordlist_block_mode(self):
        for index in range(self.__max_threads):
            if self.__active_threads > self.__max_threads:
                self.__threads_queue.get().join()
                self.__active_threads -= 1
            wordlist_block_thread = bftool.ThreadHandler.ThreadHandler(self.__wordlist_handler,
                                                                       self.__function, self.__print_queue)
            self.__threads_queue.put(wordlist_block_thread)
            wordlist_block_thread.start()
            self.__active_threads += 1
        while self.__active_threads > 0:
            self.__threads_queue.get().join()
            self.__active_threads -= 1

    def __arguments_mode_function(self, *args):
        result = self.__function(*args)
        if result is not None:
            self.__print_queue.put(result)

    def _arguments_block_mode(self):
        for arguments in self.__wordlist_handler:
            if self.__active_threads >= self.__max_threads:
                # print(self.__active_threads)
                self.__threads_queue.get().join()
                self.__active_threads -= 1
            arguments_thread = threading.Thread(target=self.__arguments_mode_function, args=arguments)
            self.__threads_queue.put(arguments_thread)
            arguments_thread.start()
            self.__active_threads += 1
        while self.__active_threads > 0:
            self.__threads_queue.get().join()
            self.__active_threads -= 1

    def run(self):
        if self.__mode == bftool.Modes.WORDLIST_BLOCK:
            self._wordlist_block_mode()
        elif self.__mode == bftool.Modes.BASIC_MODE:
            self._arguments_block_mode()
        self.__print_queue.put(f"* Process {self.__process_id} - Done")
        exit(-1)
