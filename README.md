# BruteForce Tool (bftool)
 Modular fuzzing tool

# Description
Module and script that handle different types of iterations over python iterable objects

# Usage
## As Script
Use `bftool` as a script in the command line
### Get script usage
```bash
python38 -m bftool --help
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

```bash
python38 -m bftool -w usernames -w password ./example.py check_creds
```

### Handle more Threads/Processes
By default `bftool` always spawn at least one process per execution, you can increase this number with the flags `-mp` and `--max-processes`
Inside each process can spawn Threads, by default is only one Thread per process, you can change this with the flags `-mt` and `--max-threads`
### Modes
Currently `bftool` only has two modes

* `arguments`  (enabled by default): This mode iterates over the arguments wordlist directly it means that for each argument entry it will spawn a thread
* `wordlist`: This mode is used to divide in a sub-wordlist the wordlist that was given to a spawned process it means that if a  process was spawned with a wordlist of length 10, if the user specify the max  number of threads to a number for example 5 it will divide the wordlist in 5 sub-wordlists and spawn a threads to each one
## Notes
* In the order that you specify the wordlists is the order that they are going be passed to the function, it means if you have a function `check_login(username, password)` in the moment to specify the wordlist you will gonna put them like `python38 -m bftool -w  usernames -w passwords ./example.py check_login`
* Remember that this script DO NOT sanitize the scripts you enter
## Installation

1. `git clone https://github.com/shoriwe/bftool.git`
2. `bftool`
3. `python38 setup.py install`
