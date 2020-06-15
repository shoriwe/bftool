import threading
import types
import multiprocessing


# Only a way to handle threads inside processes (useful when can read the entire wordlist)
class ThreadHandler(threading.Thread):
    def __init__(self, wordlist: tuple, function_: types.FunctionType, print_queue: multiprocessing.Queue):
        # Initialize the original thread elements
        threading.Thread.__init__(self)
        self.__wordlist = wordlist
        self.__function = function_
        self.__print_queue = print_queue

    def run(self):
        for arguments in self.__wordlist:
            result = self.__function(*arguments)
            if result:
                self.__print_queue.put(result)
        exit(-1)
