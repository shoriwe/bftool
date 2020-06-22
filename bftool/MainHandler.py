import multiprocessing
import time
import threading
import sys
import bftool
import bftool.ArgumentConstructor
import bftool.WordlistHandler
import bftool.ProcessHandler


# High level class to handle the distribution of execution of a python function
class MainHandler(object):
    """This class provide a high level interface for the exection distribution of a python function, it is
    the main core of the module"""
    def __init__(self):
        # Wordlist distributed processes
        self.__processes = []
        self.__print_queue = multiprocessing.Queue()
        self.__finish = False

    # Use this in win32 system as it has trouble using multiprocessing.Process().start()
    def start_win32_process(self, process: multiprocessing.Process):
        """Only a Windows friendly way to start a process"""
        process_thread = threading.Thread(target=process.run, )
        self.__processes.append(process_thread)

    # Use this function to handle prints
    def print_queue_handler(self):
        """This need to run in the background as it is the one that print all
        the results that the print_queue contains"""
        while not self.__finish:
            print(self.__print_queue.get())
        while not self.__print_queue.empty():
            print(self.__print_queue.get())
    
    # Use this function to start bftool
    def main(self, arguments: bftool.ArgumentConstructor.Arguments = None):
        """This function activates the MainHandler, It distributes the function in the
         specified processes and threads. To understand how it's arguments can be prepared, please check
         bftool.ArgumentConstructor.Arguments"""
        total_time = time.time()
        # If the user use bftool as a module he may want to specify a custom set of arguments
        if arguments is None:
            arguments = bftool.get_arguments()

        # Get the function to be used by the handlers
        function_ = arguments.function

        # Thanks to this it is possible to distribute the input arguments to multiple threads in a thread safe manner
        wordlist_queue = multiprocessing.Queue()

        # Start filling the queue with the arguments for the functions
        wordlist_queue_thread = threading.Thread(target=bftool.arguments_queue_handler,
                                                 args=(wordlist_queue, arguments.wordlist_handler)
                                                 )
        wordlist_queue_thread.start()

        self.__print_queue.put("--- Starting child processes ---")
        # Start the pring queue handler
        print_queue_thread = threading.Thread(target=self.print_queue_handler, )
        print_queue_thread.start()

        processes_setup_time = time.time()

        # Preparing all child processes
        for index in range(1, arguments.maximum_number_of_concurrent_processes+1):
            process_handler = bftool.ProcessHandler.ProcessHandler(index, function_, wordlist_queue,
                                                                   arguments.maximum_number_of_process_threads,
                                                                   arguments.fuzzing_mode,
                                                                   self.__print_queue)
            if sys.platform == "win32":
                self.start_win32_process(process_handler)
            else:
                self.__processes.append(process_handler)

            self.__print_queue.put(f"* Process with ID {index} - Prepared")
        processes_setup_time = time.time() - processes_setup_time
        self.__print_queue.put("--- All processes were prepared ---")
        self.__print_queue.put("--- Waiting to finish ---")
        fuzzing_time = time.time()
        # Starting all the processes
        for process in self.__processes:
            process.start()
        # Waiting all processes to finish
        for process_handler in self.__processes:
            process_handler.join()
        fuzzing_time = time.time() - fuzzing_time
        wordlist_queue_thread.join()
        total_time = time.time() - total_time
        self.__print_queue.put("--- END ---")
        self.__print_queue.put(f"Time setting up the processes: {processes_setup_time}")
        self.__print_queue.put(f"Time fuzzing: {fuzzing_time}")
        self.__print_queue.put(f"Total time: {total_time}")
        # Kill switch
        self.__finish = True
        print_queue_thread.join()
        exit(0)
