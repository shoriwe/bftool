import threading
import types
import multiprocessing


# Only a way to handle threads inside processes (useful when can read the entire wordlist)
class ThreadHandler(threading.Thread):
    def __init__(self, wordlist: tuple, function_: types.FunctionType, active_threads: multiprocessing.Value):
        # Initialize the original thread elements
        threading.Thread.__init__(self)
        self.__wordlist = wordlist
        self.__function = function_
        self.__active_threads = active_threads

    def run(self):
        for arguments in self.__wordlist:
            self.__function(*arguments)
        self.__active_threads.value -= 1
        exit(-1)
