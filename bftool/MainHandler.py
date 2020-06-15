import bftool
import multiprocessing
import threading
import sys


class MainHandler(object):
    def __init__(self):
        # Wordlist distributed processes
        self.__processes = []
        self.__finish = False

    # Use this in win32 system as it has trouble using multiprocessing.Process().start()
    def start_win32_process(self, process: multiprocessing.Process):
        process_thread = threading.Thread(target=process.run, )
        self.__processes.append(process_thread)
        process_thread.start()

    # Use this function to handle prints
    def print_queue_handler(self, print_queue: multiprocessing.Queue):
        while not self.__finish:
            print(print_queue.get())
        exit(-1)

    def main(self):
        arguments = bftool.get_arguments()

        # Get the function to be used by the handlers
        module = bftool.import_module_from_path(arguments.module_path)
        function_ = getattr(module, arguments.function_name)

        numeric_mode = bftool.Modes.WORDLIST_BLOCK if arguments.mode == "wordlist" else bftool.Modes.BASIC_MODE

        wordlist = bftool.merge_wordlists(*bftool.get_wordlists(arguments.wordlist))

        if arguments.max_processes > 1:
            wordlists = bftool.wordlist_divider(wordlist, arguments.max_processes)
        else:
            wordlists = [wordlist]

        print_queue = multiprocessing.Queue()
        
        print("--- Starting child processes ---")
        for index, sub_wordlist in enumerate(wordlists):
            process_handler = bftool.ProcessHandler(function_, sub_wordlist,
                                                    arguments.max_threads, numeric_mode, print_queue)
            if sys.platform == "win32":
                self.start_win32_process(process_handler)
            else:
                process_handler.start()
                self.__processes.append(process_handler)
                print(f"* Process with ID {index} - Started")
        print("--- Waiting to finish ---")
        print("--- Starting printing QUEUE --- ")
        queue_thread = threading.Thread(target=self.print_queue_handler, args=(print_queue,))
        queue_thread.start()
        if sys.platform == "win32":
            print("OS: Windows\nNo end will be printed so be careful to end the fuzzing tool by your self (Control-C)")
        for process_handler in self.__processes:
            process_handler.join()
        if sys.platform != "win32":
            print("-----END-----")
            self.__finish = True
        queue_thread.join()
        exit(0)
