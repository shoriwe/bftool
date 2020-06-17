import multiprocessing
import threading
import sys
import bftool
import bftool.WordlistHandler
import bftool.ProcessHandler


class MainHandler(object):
    def __init__(self):
        # Wordlist distributed processes
        self.__processes = []
        self.__print_queue = multiprocessing.Queue()
        self.__finish = False

    # Use this in win32 system as it has trouble using multiprocessing.Process().start()
    def start_win32_process(self, process: multiprocessing.Process):
        process_thread = threading.Thread(target=process.run, )
        self.__processes.append(process_thread)

    # Use this function to handle prints
    def print_queue_handler(self):
        while not self.__finish:
            print(self.__print_queue.get())
        while not self.__print_queue.empty():
            print(self.__print_queue.get())

    def main(self):
        arguments = bftool.get_arguments()

        # Get the function to be used by the handlers
        module = bftool.import_module_from_path(arguments.module_path)
        function_ = getattr(module, arguments.function_name)

        wordlist_handler = bftool.WordlistHandler.WordlistHandler()
        wordlist_queue = multiprocessing.Queue()

        numeric_mode = bftool.Modes.WORDLIST_BLOCK if arguments.mode == "wordlist" else bftool.Modes.BASIC_MODE

        if arguments.wordlist:
            wordlist_handler.wordlist_from_files(*arguments.wordlist)
        if arguments.bruteforce:
            wordlist_handler.pure_bruteforce_setup(*arguments.bruteforce)
        wordlist_handler.setup()

        # Start filling the queue
        wordlist_queue_thread = threading.Thread(target=bftool.arguments_queue_handler, args=(wordlist_queue, wordlist_handler))
        wordlist_queue_thread.start()

        self.__print_queue.put("--- Starting child processes ---")
        queue_thread = threading.Thread(target=self.print_queue_handler, )
        queue_thread.start()
        for index in range(1, arguments.max_processes+1):
            process_handler = bftool.ProcessHandler.ProcessHandler(index, function_, wordlist_queue,
                                                                   arguments.max_threads,
                                                                   numeric_mode,
                                                                   self.__print_queue)
            if sys.platform == "win32":
                self.start_win32_process(process_handler)
            else:
                self.__processes.append(process_handler)

            self.__print_queue.put(f"* Process with ID {index} - Prepared")
        self.__print_queue.put("--- All processes were prepared ---")
        self.__print_queue.put("--- Waiting to finish ---")
        for process in self.__processes:
            process.start()
        for process_handler in self.__processes:
            process_handler.join()
        self.__finish = True
        wordlist_queue_thread.join()
        queue_thread.join()
        self.__print_queue.put("--- END ---")
        exit(0)
