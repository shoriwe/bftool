# BruteForce Tool (bftool)
 Modular fuzzing tool

# Description
Module and script that handle different types of iterations over python iterable objects
# Requiriments
* Python >= 3.8
# Usage
## As Script
Use `bftool` as a script in the command line
### Get script usage
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
                        Mode to use during the function execution (way to divide the threads) (default=arguments)
```

### Quick example
Writing a script with only a function in it like in a file called `example.py`

The implemented function just need to return the string that you want to print when success, the printing queue will handle it
```python
def check_creds(username: str, password: str):
    # Using
    login_result = login_in_X_service(username, password) # for example login to a X service
    if login_result.success: # If we could login, we want to print the valid credentials
       return f"[+] {username} - {password}" # By returning it, the printing queue will handle it
```
Can import the function `check_creds` in the `bftool` with

```
python -m bftool -w usernames -w password ./example.py check_creds
```

Expected output

```
--- Starting printing QUEUE --- 
--- Starting child processes ---
* Process with ID 1 - Started
--- Waiting to finish ---
[<ProcessHandler name='ProcessHandler-1' pid=2148 parent=2146 started>]
admin:password
john:password1234
-----END-----
```

### Handle more Threads/Processes
By default `bftool` always spawn at least one process per execution, you can increase this number with the flag `-mp MAX_NUMBER_OF_PROCESSES` (`--max-processes MAX_NUMBER_OF_PROCESSES`), just remember that this flag divide the provided wordlist in those threads
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
This mode is used to divide in smaller wordlists the wordlist that was given to a spawned process, it means that if a process was spawned with a wordlist of length 10, if the user specify the max number of threads to a number for example 5 it will divide the wordlist in 5 sub-wordlists and spawn threads for each one
##### Explanation
This mode spawn new threads for blocks of wordlist

For example, if we have the wordlist `names`
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
The function `say_name(name: str)`
\
And we set the `--max-threads` to for example `2`, `bftool` will divide the given wordlist in two small wordlists
\
`virtual_wordlist_1`
```
john
alice
bob
feix
phineas
```
`virtual_wordlist_2`
```
ferb
rick
morty
bob
patrick
```

`bftool` is going to processed each virtual wordlist using in an indepent thread.
\
The `Python` equivalent will be
```python
def wordlist_handler(wordlist: tuple):
    for name in wordlist:
        say_name(wordlist)

for virtual_wordlist in virtual_wordlist:
    threading.Thread(target=wordlist_handler, args=(virtual_wordlist, )).start()
```
## Example fuzz functions
Comming soon
## As Module
No documentation available yet
# Notes
* If you have troubles loading big wordlists, you can divide it in smaller wordlists for different processes with `-mp NUMBER_PROCESSES` option. **WARNING** if you want to fuzz in a linear way (without spawning a thread for each word(s)) this option is not going to help you (you may want to divide your wordlist in smaller wordlists files).
* In the order that you specify the wordlists is the order that they are going be passed to the function, it means if you have a function `check_login(username, password)` in the moment to specify the wordlist you will gonna put them like `python -m bftool -w  usernames -w passwords ./example.py check_login`
* Remember that this script DO NOT sanitize the scripts you enter
# Installation

## Manual
1. `git clone https://github.com/shoriwe/bftool.git`
2. `cd bftool`
3. `python setup.py install`
## pip
Comming soon
# Bugs and suggestions
## Bugs
Please report bugs in the issues section I will try to fix at least one in the same day you report it.
## Suggestions
If you have any suggestion for new features, also leave them in the issue section or create the proper 
branch, add what do you want and request a pull request
