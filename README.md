# arsenal-ng

issued from [https://github.com/Orange-Cyberdefense/arsenal](https://github.com/Orange-Cyberdefense/arsenal)

## TODO
* Dev a MouselessVerticalScroll
* guing
  * if command has no vars don't launch CmdEditModal
* TmuxModal
  * reload previously selected params
* GlobalVarsEditModal
  * add the possibility to create a global var

#

## tmux mode

Previous mode was working only when only one session was running. Since libtmux does not provide a way to identify tmux session the code is running in.


This new mode will need a `pane_path` which pattern is `<session_name>:<window_name>:[<pane_id>]`

Regarding `pane_path` :
- session identified by `session_name` must exist.
- if windows identified by `window_name`: 
  - does not exist: it will be created then pane number is ignored if specified
  - exist and `pane_id`:
    - is not specified: command will be sent to all panes in the window
    - does not exist: a new pane will be created (similar to previous mode)
    - exist: guess what

Note: within tmux session `prefix-q` willdisplay panes number

```
# will send command to all pane in arsenal-windows (windows creation needed) 
./run --tmux-new tmux-pentest:arsenal-windows:

# will send command to a new pane
./run --tmux-new tmux-pentest:arsenal-windows:99

# will send command to pane 3
./run --tmux-new tmux-pentest:arsenal-windows:3
```