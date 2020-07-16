import multiprocessing
import time
import threading
import sys
import collections
import argparse

from .Arguments import Arguments
from .Process import Process
from .Modes import ARGUMENTS_MODE
from .Modes import WORDLIST_MODE


__all__ = ["Runner", "_get_arguments", "_queue_arguments_loader"]


# Default argument capture for the main function
def _get_arguments() -> Arguments:
    """Default function to prepare the arguments for the `Runner` during it's execution in a terminal

    Returns:
        - bftool.Arguments with all  the configurations provided by the user
    """
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("-mt", "--max-threads",
                                 help="Maximum number of threads per process", default=1, type=int)
    argument_parser.add_argument("-mp", "--max-processes",
                                 help="Maximum number of process to have active at the same time",
                                 default=ARGUMENTS_MODE, type=int)
    argument_parser.add_argument("-w", "--wordlist", help="File wordlist to use"
                                                          " based on \"[ARGUMENT_INDEX, ARGUMENT_NAME]:file_path\"",
                                 action="append", default=[])
    argument_parser.add_argument("-b", "--bruteforce",
                                 help="Generate a virtual wordlist based on \
                                 rules \"[ARGUMENT_INDEX, ARGUMENT_NAME]:chars=...,minlength=...,maxlength=...\"",
                                 action="append", default=[])
    argument_parser.add_argument("-m", "--mode",
                                 help="Mode to use during the function execution (way to divide the threads)",
                                 choices=("wordlist", "arguments"), default="arguments")
    argument_parser.add_argument("-sf", "--success-function",
                                 help="Function to pass the success result (default is 'print')",
                                 default=print)
    argument_parser.add_argument('--debug-off',
                                 help="Do not print the setup messages",
                                 default=False,
                                 action="store_true")
    argument_parser.add_argument("script_path", help="Python script to import")
    argument_parser.add_argument("function_name", help="Name of the function implemented in the python script to use")
    parsed_arguments = argument_parser.parse_args()
    if parsed_arguments.mode == "wordlist":
        parsed_arguments.mode = WORDLIST_MODE
    elif parsed_arguments.mode == "arguments":
        parsed_arguments.mode = ARGUMENTS_MODE
    arguments = Arguments(
        script_path=parsed_arguments.script_path,
        debug=not parsed_arguments.debug_off,
        function_name=parsed_arguments.function_name,
        success_function=parsed_arguments.success_function,
        files_wordlists=dict(wordlist.split(":") for wordlist in parsed_arguments.wordlist),
        bruteforce_rules_wordlists=dict(wordlist.split(":") for wordlist in parsed_arguments.bruteforce),
        maximum_number_of_concurrent_processes=parsed_arguments.max_processes,
        maximum_number_of_process_threads=parsed_arguments.max_threads,
        fuzzing_mode=parsed_arguments.mode,
    )
    return arguments


def _queue_arguments_loader(arguments_queue: multiprocessing.Queue, master_wordlist: iter):
    """Fill the `arguments_queue` of the `Main` with the arguments provided by `Wordlist`


    Arguments:
        - arguments_queue: multiprocessing.Queue that is shared with active processes
        - wordlist_: bftool.Wordlist.Wordlist object
    """
    for argument in master_wordlist:
        arguments_queue.put(argument)
    exit(0)


# High level class to handle the distribution of execution of a python function
class Runner(object):
    """This class provide a high level interface for the execution distribution of a python function, it is
    the main core of the module"""

    def __init__(self):
        self.__debug_setup = True
        # Wordlist distributed processes
        self.__processes = []
        self.__print_queue = multiprocessing.Queue()
        self.__finish = False

    # Use this in win32 system as it has trouble using multiprocessing.Process().start()
    def start_win32_process(self, process: multiprocessing.Process):
        """Only a Windows friendly way to start a process

        Arguments:
            - process: process to start
        """
        process_thread = threading.Thread(target=process.run, )
        self.__processes.append(process_thread)

    # Use this function to handle prints
    def success_queue_(self, success_function: collections.abc.Callable):
        """This need to run in the background as it is the one that print all
        the results that the print_queue contains"""
        while not self.__finish:
            success_function(self.__print_queue.get())
        while not self.__print_queue.empty():
            success_function(self.__print_queue.get())

    def _print_setup(self, message: str):
        if self.__debug_setup:
            print(message)

    # Use this function to start bftool
    def main(self, arguments: Arguments = None):
        """This function activates the Main, It distributes the function in the
         specified processes and threads. To understand how it's arguments can be prepared, please check
         `bftool.ArgumentConstructor.Arguments`

         Arguments:
             - arguments: bftool.ArgumentConstructor.Arguments
        """
        total_time = time.time()
        # If the user use bftool as a module he may want to specify a custom set of arguments
        if arguments is None:
            arguments = _get_arguments()
        arguments.is_valid()
        self.__debug_setup = arguments.debug

        # Get the function to be used by the s
        function_ = arguments.function

        # Thanks to this it is possible to distribute the input arguments to multiple threads in a thread safe manner
        wordlist_queue = multiprocessing.Queue()

        # Start filling the queue with the arguments for the functions
        wordlist_queue_thread = threading.Thread(target=_queue_arguments_loader,
                                                 args=(wordlist_queue, arguments.master_wordlist)
                                                 )
        wordlist_queue_thread.start()

        self._print_setup("--- Starting child processes ---")
        # Start the print queue
        print_queue_thread = threading.Thread(target=self.success_queue_, args=(arguments.success_function,))
        print_queue_thread.start()

        processes_setup_time = time.time()

        # Preparing all child processes
        for index in range(1, arguments.maximum_number_of_concurrent_processes + 1):
            process_ = Process(index,
                               function_,
                               wordlist_queue,
                               arguments.maximum_number_of_process_threads,
                               arguments.fuzzing_mode,
                               self.__print_queue)
            if sys.platform == "win32":
                self.start_win32_process(process_)
            else:
                self.__processes.append(process_)

            self._print_setup(f"* Process with ID {index} - Prepared")
        processes_setup_time = time.time() - processes_setup_time
        self._print_setup("--- All processes were prepared ---")
        self._print_setup("--- Waiting to finish ---")
        fuzzing_time = time.time()
        # Starting all the processes
        for process in self.__processes:
            process.start()
        # Waiting all processes to finish
        for process_ in self.__processes:
            process_.join()
        fuzzing_time = time.time() - fuzzing_time
        wordlist_queue_thread.join()
        total_time = time.time() - total_time
        self._print_setup("--- END ---")
        self._print_setup(f"Time setting up the processes: {processes_setup_time}")
        self._print_setup(f"Time fuzzing: {fuzzing_time}")
        self._print_setup(f"Total time: {total_time}")
        # Kill switch
        self.__finish = True
        print_queue_thread.join()
        exit(0)
