# arsenal-ng

issued from [https://github.com/Orange-Cyberdefense/arsenal](https://github.com/Orange-Cyberdefense/arsenal)

# Install

## local
```bash
pipx install .
```

## from git repo
```bash
pipx install git+https://github.com/jubeaz/arsenal-ng.git
```

## TODO
* work on options
* Dev a MouselessVerticalScroll
* guing
  * if command has no vars don't launch CmdEditModal
* Tmux
  * There might exist a bug since two windows can have the same name and the use of `select_window` might return the wrong one.
* Global vars edition:
  * add the possibility to create a global var




# CSS
## green monochrome

# debug
```
python3 -m venv venv
source .venv/bin/activate
pip install -e .
```

in vscode
```
Ctrl + Shift + p
Python: Select Interpreter
Python xxx ('venv': venv) ./venv/bin/python
```