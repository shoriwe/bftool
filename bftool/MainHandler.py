import bftool
import multiprocessing
import threading
import sys


class MainHandler(object):
    def __init__(self):
        # Wordlist distributed processes
        self.__processes = []
        self.__print_queue = multiprocessing.Queue()

    # Use this in win32 system as it has trouble using multiprocessing.Process().start()
    def start_win32_process(self, process: multiprocessing.Process):
        process_thread = threading.Thread(target=process.run, )
        self.__processes.append(process_thread)
        process_thread.start()

    # Use this function to handle prints
    def print_queue_handler(self):
        while True:
            print(self.__print_queue.get())

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

        print("--- Starting child processes ---")
        for index, sub_wordlist in enumerate(wordlists):
            process_handler = bftool.ProcessHandler(function_, sub_wordlist,
                                                    arguments.max_threads, numeric_mode, self.__print_queue)
            if sys.platform == "win32":
                self.start_win32_process(process_handler)
            else:
                process_handler.start()
                self.__processes.append(process_handler)
                print(f"* Process with ID {index} - Started")
        print("--- Waiting to finish ---")
        queue_thread = threading.Thread(target=self.print_queue_handler, )
        queue_thread.start()
        if sys.platform == "win32":
            print("OS: Windows\nNo end will be printed so be careful to end the fuzzing tool by your self (Control-C)")
        for process_handler in self.__processes:
            process_handler.join()
        queue_thread.join()
        exit(0)
