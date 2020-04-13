# BruteForce Tool (bftool)
 Modular fuzzing tool

# Description
Module and script that handle different types of iterations over python iterable objects
# Requiriments
* Python >= 3.8
# Usage
```
fuzzer@linux:~$ python -m bftool --help
usage: __main__.py [-h] [-mt MAX_THREADS] [-mp MAX_PROCESSES] -w WORDLIST [-m {wordlist,arguments}] module_path function_name

positional arguments:
  module_path           Path to the python module to the function to use
  function_name         Name of the function to use

optional arguments:
  -h, --help            show this help message and exit
  -mt MAX_THREADS, --max-threads MAX_THREADS
                        Maximum number of threads per process (if mode is set to wordlist block, this will be also the worlist division number)
  -mp MAX_PROCESSES, --max-processes MAX_PROCESSES
                        Maximum number of process to have active at the same time
  -w WORDLIST, --wordlist WORDLIST
                        Wordlist to use (can be used more than once)
  -m {wordlist,arguments}, --mode {wordlist,arguments}
                        Mode to use during the function execution (way to divide the threads)
```
## As Script
Use `bftool` as a script in the command line
### Get script usage
```
python -m bftool --help
```
### Fuzzing
Writing a script with only a function in it like in a file `example.py`

```python
def check_creds(username: str, password: str):
    # Using
    login_object = login(username, password)
    if login_object.success:
       print(f"[+] {username} - {password}")
```
Can import the function `check_creds` in the `bftool` with

```
python -m bftool -w usernames -w password ./example.py check_creds
```

### Handle more Threads/Processes
By default `bftool` always spawn at least one process per execution, you can increase this number with the flags `-mp` and `--max-processes`
Inside each process can spawn Threads, by default is only one Thread per process, you can change this with the flags `-mt` and `--max-threads`
### Modes
Currently `bftool` only has two modes

* `arguments`  (enabled by default): This mode iterates over the arguments wordlist directly it means that for each argument entry it will spawn a thread
* `wordlist`: This mode is used to divide in a sub-wordlist the wordlist that was given to a spawned process it means that if a  process was spawned with a wordlist of length 10, if the user specify the max  number of threads to a number for example 5 it will divide the wordlist in 5 sub-wordlists and spawn a threads to each one
## As Module
No yet supported
# Notes
* In the order that you specify the wordlists is the order that they are going be passed to the function, it means if you have a function `check_login(username, password)` in the moment to specify the wordlist you will gonna put them like `python38 -m bftool -w  usernames -w passwords ./example.py check_login`
* Remember that this script DO NOT sanitize the scripts you enter
# Installation

## Manual
1. `git clone https://github.com/shoriwe/bftool.git`
2. `bftool`
3. `python setup.py install`
## pip
Comming soon
