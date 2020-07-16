import threading
import types
import queue
import multiprocessing


__all__ = ["Thread"]


# Only a way to handle threads inside processes
class Thread(threading.Thread):
    """Independent Thread, that did not spawn a independent thread for each function execution as it is in self the
    thread that calls it, in other words, it is the equivalent of `bftool.Process` in arguments mode but without
    spawning an independent thread for each function call"""
    def __init__(self, wordlist_queue: multiprocessing.Queue,
                 function_: types.FunctionType, print_queue: multiprocessing.Queue):
        """
            - wordlist_queue: the master wordlist queue
            - function_: the function that is going to be executed
            - print_queue: the printing queue to put the results
        """
        # Initialize the original thread elements
        threading.Thread.__init__(self)
        self.__wordlist_queue = wordlist_queue
        self.__function = function_
        self.__print_queue = print_queue

    # Thread runner
    def run(self):
        """This function is executed when the user calls `Thread.start()`"""
        while True:
            try:
                arguments = self.__wordlist_queue.get(True, timeout=5)
            except queue.Empty:
                break
            result = self.__function(*arguments)
            if result is not None:
                self.__print_queue.put(result)
        exit(0)
