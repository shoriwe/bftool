# BFTOOL
[![Maintened](https://img.shields.io/badge/Maintained-Yes-green.svg)](https://github.com/shoriwe/bftool)
[![Maintened](https://img.shields.io/badge/Pypi-Yes-blue.svg)](https://pypi.org/project/bftool-pkg-sulcud/)
[![PyPI version](https://badge.fury.io/py/bftool-pkg-sulcud.svg)](https://pypi.org/project/bftool-pkg-sulcud/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/shoriwe/bftool/blob/master/LICENSE)
[![Downloads](https://img.shields.io/pypi/dd/bftool-pkg-sulcud?color=green)](https://pypi.org/project/bftool-pkg-sulcud/)

![Logo](https://raw.githubusercontent.com/shoriwe/bftool/master/logo/logo_size_invert.jpg)

# Index
- [Description](#description)
- [Requirements](#requirements)
- [Usage](#usage)
    * [As Script](#as-script)
        * [Get script usage](#get-script-usage)
        * [Quick example](#quick-example)
        * [Bruteforce rules](#bruteforce-rules)
    * [As Module](#as-module)
- [Concepts](#concepts)
    * [Handle more Threads/Processes](#handle-more-threadsprocesses)
    * [Modes](#modes)
        * [Arguments](#arguments--enabled-by-default)
        * [Wordlist](#wordlist)
- [Examples](#examples)
- [Notes](#notes)
- [Installation](#installation)
    * [Manual](#manual)
    * [pip](#pip)
- [Bug and suggestions](#bugs-and-suggestions)
# Description
`bftool` is a python module, and script, that facilitate the implementation of custom fuzzing against anything, by providing
a high level API to distribute a python function in processes and/or threads, so the only a developer need to worry
is in the fuzzing function and not in how to distribute it's execution
# Requirements
* Python >= 3.6
# Usage
## As Script
Use `bftool` as a script in the command line
### Get script usage
```
fuzzer@linux:~$ python -m bftool --help
usage: bftool-run.py [-h] [-mt MAX_THREADS] [-mp MAX_PROCESSES] [-w WORDLIST]
                     [-b BRUTEFORCE] [-m {wordlist,arguments}]
                     [-sf SUCCESS_FUNCTION] [--debug-off]
                     script_path function_name

positional arguments:
  script_path           Python script to import
  function_name         Name of the function implemented in the python script
                        to use

optional arguments:
  -h, --help            show this help message and exit
  -mt MAX_THREADS, --max-threads MAX_THREADS
                        Maximum number of threads per process
  -mp MAX_PROCESSES, --max-processes MAX_PROCESSES
                        Maximum number of process to have active at the same
                        time
  -w WORDLIST, --wordlist WORDLIST
                        File wordlist to use based on "[ARGUMENT_INDEX,
                        ARGUMENT_NAME]:file_path"
  -b BRUTEFORCE, --bruteforce BRUTEFORCE
                        Generate a virtual wordlist based on rules
                        "[ARGUMENT_INDEX,
                        ARGUMENT_NAME]:chars=...,minlength=...,maxlength=..."
  -m {wordlist,arguments}, --mode {wordlist,arguments}
                        Mode to use during the function execution (way to
                        divide the threads)
  -sf SUCCESS_FUNCTION, --success-function SUCCESS_FUNCTION
                        Function to pass the success result (default is
                        'print')
  --debug-off           Do not print the setup messages
```

### Quick example
Writing a script with only a function in it like in a file called `example.py`

The implemented function just need to return the string that you want to print when success, the printing queue will handle the call to print
```python
def check_creds(username: str, password: str):
    # Using
    login_result = login_in_X_service(username, password) # for example login to a X service
    if login_result.success: # If we could login, we want to print the valid credentials
       return f"[+] {username} - {password}" # By returning it, the printing queue will handle it
```
Can import the function `check_creds` in the `bftool` with:

By passing arguments by the argument name (like by passing it with kargs)

```
python -m bftool -w username:usernames.txt -w password:passwords.txt ./example.py check_creds
```
Or with:

By passing the arguments by index
```
python -m bftool -w 0:usernames.txt -w 1:passwords.txt ./example.py check_creds
```
Expected output

```
--- Starting child processes ---
* Process with ID 1 - Started
--- All processes were prepared ---
--- Waiting to finish ---
[+] admin - password
[+] john - password1234
* Process 1 - Done
--- END ---
Time setting up the processes: 0.001027822494506836
Time fuzzing: 15.191009759902954
Total time: 15.199022769927979
```
### Bruteforce rules
You can force `bftool` to create a virtual wordlist of custom chars combined with cartesian product of a specific length by providing the `-b` (`--bruteforce`) argument 

```
python -m bftool -b argument_name:chars=abcdef,minlength=10,maxlength=1000 script.py function_
```

- This feature is really fast as  it generates the wordlist on the fly
- It's functionality is very similar to the wordlist specification option, the only different is that it receive as input the wordlist generation rule

## As Module
You can use it as module by creating an `Argument` object and a `MainHandler`

```python
import bftool
import time


def check(word1, word2):
    time.sleep(2)
    if word1 == word2 and word1 == word1[::-1]:
        return f"{word1} - {word2}"


def success_print(result: str):
    print("[+]", result)


def main():
    wordlist = {"word1": "chars=qwertyuiopasdfghjklzxcvbnm,minlength=1,maxlength=2",
                "word2": "chars=qwertyuiopasdfghjklzxcvbnm,minlength=1,maxlength=2"}
    arguments = bftool.Arguments(check,
                                 success_function=success_print,
                                 debug=False,
                                 bruteforce_rules_wordlists=wordlist,
                                 maximum_number_of_process_threads=4,
                                 maximum_number_of_concurrent_processes=10,
                                 fuzzing_mode=bftool.Modes.WORDLIST_MODE
                                 )

    runner = bftool.Runner()
    runner.main(arguments)


if __name__ == "__main__":
    main()
```

## Concepts
### Handle more Threads/Processes
By default `bftool` always spawn at least one process per execution, you can increase this number with the flag `-mp MAX_NUMBER_OF_PROCESSES` (`--max-processes MAX_NUMBER_OF_PROCESSES`), just remember that this flag divide the provided wordlist in those processes
\
Inside each process can spawn Threads, by default is only one Thread per process, you can change this with the flag `-mt MAX_NUMBER_OF_THREADS` (`--max-threads MAX_NUMBER_OF_THREADS`)
### Modes
Currently `bftool` only has two modes

#### `arguments`  (enabled by default)
This mode iterates over the arguments wordlist directly it means that for each argument entry it will spawn a thread
##### Explanation
If you has the wordlist `names.txt`
```
john
alice
bob
feix
```
And the python function `say_name(name: str)`\
\
`bftool` will spawn one thread for each argument. In other words, it will run in parallel the function `say_name` with each `name`

The `Python` equivalent will be
```python
for name in file.readlines():
    threading.Thread(target=say_name, args=(name, )).start()
```

#### `wordlist`

##### Explanation
This mode spawn indepent thread handlers

For example, if we have the wordlist `names.txt`
```
john
alice
bob
feix
phineas
ferb
rick
morty
bob
patrick
```

`bftool` is going to processed the wordlist using independent threads.
\
The `Python` equivalent will be
```python
def wordlist_handler(wordlist_handler: Queue):
    while True:
        try:
            name = wordlist_handler.get(timeout=5)
        except Empty:
            break
        say_name(name)

for thread in available_threads:
    threading.Thread(target=wordlist_handler, args=(wordlist_handler, )).start()
```
# Examples
Here you can found some [Examples](https://github.com/shoriwe/bftool/tree/master/examples)

# Notes
* If you want to run a function that has a small time cost (like 1 seconds or less), it will be better to implement a simple for loop to run it instead of this tool
* Remember that this script DO NOT sanitize the scripts you enter
# Installation

## Manual
1. `git clone https://github.com/shoriwe/bftool.git`
2. `cd bftool`
3. `python setup.py install`
## pip
```pip install bftool-pkg-sulcud```
# Bugs and suggestions
## Bugs
Please report bugs in the issues section I will try to fix at least one in the same day you report it.
## Suggestions
If you have any suggestion for new features, also leave them in the issue section or create the proper 
branch, add what do you want and request a pull request
