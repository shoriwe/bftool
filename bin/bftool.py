import bftool
import argparse
import multiprocessing


def get_arguments():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("-mt", "--max-threads",
                                 help="Maximum number of threads per process (if mode is set to wordlist block, \
                                 this will be also the worlist division number)", default=1, type=int)
    argument_parser.add_argument("-mp", "--max-processes",
                                 help="Maximum number of process to have active at the same time",
                                 default=1, type=int)
    argument_parser.add_argument("-w", "--wordlist", help="Wordlist to use (can be used more than once)",
                                 action="append", required=True)
    argument_parser.add_argument("-m", "--mode",
                                 help="Mode to use during the function execution (way to divide the threads)",
                                 choices=("wordlist", "arguments"), default="arguments")
    # argument_parser.add_argument("-q", "--queue",
    #                             help="Queue like object to handle prints better (it need to be implemented in your file)",
    #                             default=None)
    argument_parser.add_argument("module_path", help="Path to the python module to the function to use")
    argument_parser.add_argument("function_name", help="Name of the function to use")
    return argument_parser.parse_args()


def main():
    arguments = get_arguments()

    active_processes = multiprocessing.Value("i", 0)
    active_threads = multiprocessing.Value("i", 0)

    module = bftool.import_module_from_path(arguments.module_path)
    function_ = getattr(module, arguments.function_name)
    # if arguments.queue:
    #     queue_object = getattr(module, arguments.queue)
    # else:
    #     queue_object = None
    numeric_mode = bftool.Modes.WORDLIST_BLOCK if arguments.mode == "wordlist" else bftool.Modes.BASIC_MODE

    wordlist = bftool.merge_wordlists(*bftool.get_wordlists(arguments.wordlist))

    if arguments.max_processes > 1:
        wordlists = bftool.wordlist_divider(wordlist, arguments.max_processes)
    else:
        wordlists = [wordlist]
    for sub_wordlist in wordlists:
        while active_processes.value > arguments.max_processes:
            pass
        process_handler = bftool.ProcessHandler(function_, sub_wordlist, active_threads,
                                                active_processes, arguments.max_threads, numeric_mode)
        process_handler.start()
    while active_threads.value > 0:
        pass
    # if queue_object:
    #    while True:
    #        queue_value = queue_object.get()
    #        print(queue_value)
    # else:
    #    while active_threads.value > 0:
    #        pass


if __name__ == "__main__":
    main()
