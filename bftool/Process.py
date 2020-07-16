import threading
import types
import multiprocessing
import queue

from Thread import Thread

from .Modes import ARGUMENTS_MODE
from .Modes import WORDLIST_MODE


__all__ = ["Process"]


# This class is a high level API implemented by inheritance with the python multiprocessing.Process
class Process(multiprocessing.Process):
    """This class provide a high level API to handle the distribution of threads inside a independent process"""
    def __init__(self,
                 process_id: int,
                 function_: types.FunctionType, wordlist_queue: multiprocessing.Queue,
                 max_threads: int, mode: int,
                 print_queue):
        """
            - process_id: ID of the process
            - function_: function that is goning to be passed to the threads
            - wordlist_queue: the master wordlist queue
            - max_threads: The maximum number of concurrent threads for this process
            - mode: The mode in which distribute the execution
            - print_queue: master print queue
        """
        multiprocessing.Process.__init__(self)
        self.__process_id = process_id
        self.__function = function_
        self.__wordlist_queue = wordlist_queue
        self.__active_threads = 0
        self.__max_threads = max_threads
        self.__mode = mode
        self.__threads_queue = queue.Queue()
        self.__print_queue = print_queue

    #  for the wordlist mode
    def _wordlist_block_mode(self):
        """This is used when the user specify the mode WORDLIST, it spawns independent threads that handle function"""
        for index in range(self.__max_threads):
            if self.__active_threads > self.__max_threads:
                self.__threads_queue.get().join()
                self.__active_threads -= 1
            wordlist_block_thread = Thread(self.__wordlist_queue,
                                           self.__function, self.__print_queue)
            self.__threads_queue.put(wordlist_block_thread)
            wordlist_block_thread.start()
            self.__active_threads += 1
        while self.__active_threads > 0:
            self.__threads_queue.get().join()
            self.__active_threads -= 1

    #  for the execution of the the specified function in a independent thread (ARGUMENTS mode)
    def __arguments_mode_function(self, *args):
        """ for the execution of the the specified function in a independent thread (`ARGUMENTS` mode)

        Arguments:
            - args: arguments that are going to be passed to the function
        """
        result = self.__function(*args)
        if result is not None:
            self.__print_queue.put(result)
        exit(0)

    #  for the arguments mode, it spawn an independent thread for each function execution
    def _arguments_block_mode(self):
        """ for the arguments mode, it spawn an independent thread for each function execution"""
        while True:
            try:
                arguments = self.__wordlist_queue.get(True, timeout=5)
            except queue.Empty:
                break
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

    # Runner, it start the process
    def run(self):
        """Runner, it start the process, if you are in Linux please consider to use `Process.start()`, if you are
        in Windows consider tu execute this function in a independent thread with the threading module, it could look
        like this `threading.Thread(target=Process.run, args=(*args, **kargs)).start()`"""
        if self.__mode == WORDLIST_MODE:
            self._wordlist_block_mode()
        elif self.__mode == ARGUMENTS_MODE:
            self._arguments_block_mode()
        else:
            raise KeyError("Unknown mode supplied")
        self.__print_queue.put(f"* Process {self.__process_id} - Done")
        exit(0)
