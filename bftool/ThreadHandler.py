import threading
import types
import queue
import multiprocessing


# Only a way to handle threads inside processes (useful when can read the entire wordlist)
class ThreadHandler(threading.Thread):
    def __init__(self, wordlist_queue: multiprocessing.Queue,
                 function_: types.FunctionType, print_queue: multiprocessing.Queue):
        # Initialize the original thread elements
        threading.Thread.__init__(self)
        self.__wordlist_queue = wordlist_queue
        self.__function = function_
        self.__print_queue = print_queue

    def run(self):
        while True:
            try:
                arguments = self.__wordlist_queue.get(True, timeout=5)
            except queue.Empty:
                break
            result = self.__function(*arguments)
            if result is not None:
                self.__print_queue.put(result)
        exit(0)
