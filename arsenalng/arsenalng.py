import argparse
import os
import fcntl
import termios
from shutil import copy
from curses import wrapper
from rich import print

# arsenal
from . import __version__
from arsenalng.data import config
from arsenalng.modules import check
from arsenalng.models.cheatdict import CheatDict
from arsenalng.gui.arsenalnggui import ArsenalNGGui


class ArsenalNG:
    gui = None

    def __init__(self):
        pass

    def get_args(self):
        examples = """examples:
        arsenalng
        arsenalng --copy
        arsenalng --print

        You can manage global variables with:
        >set GLOBALVAR1=<value>
        >show
        >clear

        (cmd starting with ">" are internals cmd)
        """

        parser = argparse.ArgumentParser(
            prog="arsenalng",
            description=f"arsenalng v{__version__} - Pentest command launcher",
            epilog=examples,
            formatter_class=argparse.RawTextHelpFormatter
        )

        group_out = parser.add_argument_group("output [default = prefill]")
        group_out.add_argument("-p", "--print", action="store_true", help="Print the result")
        group_out.add_argument("-o", "--outfile", action="store", help="Output to file")
        group_out.add_argument("-x", "--copy", action="store_true", help="Output to clipboard")
        group_out.add_argument("-e", "--exec", action="store_true", help="Execute cmd")
        group_out.add_argument("-t", "--tmux", action="store_true", help="Send command to tmux")
        group_out.add_argument("-c", "--check", action="store_true", help="Check the existing commands")
        group_out.add_argument("-f", "--prefix", action="store_true", help="command prefix")
        parser.add_argument("-V", "--version", action="version", version=f"%(prog)s (version {__version__})")

        return parser.parse_args()

    def run(self):
        args = self.get_args()
        # load cheatsheets
        cheatsheets = CheatDict().read_files(config.CHEATS_PATHS, config.FORMATS,
                                                config.EXCLUDE_LIST)
        if args.check:
            check.check(cheatsheets)
        else:
            self.gui = ArsenalNGGui(cheatsheets=cheatsheets, args=args) 
            self.start(args, cheatsheets)

    def start(self, args, cheatsheets):
        cmd = self.gui.run()
        if cmd is None:
            exit(0)
        elif args.copy: # OPT: Copy CMD to clipboard
            try:
                import pyperclip
                pyperclip.copy(cmd)
            except ImportError:
                pass
        elif args.print: # OPT: Only print CMD
            print(cmd)
        elif args.outfile: # OPT: Write in file
            with open(args.outfile, "w") as f:
                f.write(cmd)
        elif args.exec: # OPT: Exec
            os.system(cmd)
        else: # DEFAULT: Prefill Shell CMD
            self.prefil_shell_cmd(cmd)


    def prefil_shell_cmd(self, cmd):
        stdin = 0
        # save TTY attribute for stdin
        oldattr = termios.tcgetattr(stdin)
        # create new attributes to fake input
        newattr = termios.tcgetattr(stdin)
        # disable echo in stdin -> only inject cmd in stdin queue (with TIOCSTI)
        newattr[3] &= ~termios.ECHO
        # enable non canonical mode -> ignore special editing characters
        newattr[3] &= ~termios.ICANON
        # use the new attributes
        termios.tcsetattr(stdin, termios.TCSANOW, newattr)
        # write the selected command in stdin queue
        try:
            for c in cmd:
                fcntl.ioctl(stdin, termios.TIOCSTI, c)
        except OSError:
            message = "========== OSError ============\n"
            message += "Arsenal needs TIOCSTI enable for running\n"
            message += "Please run the following commands as root to fix this issue on the current session :\n"
            message += "sysctl -w dev.tty.legacy_tiocsti=1\n"
            message += "If you want this workaround to survive a reboot,\n" 
            message += "add the following configuration to sysctl.conf file and reboot :\n"
            message += 'echo "dev.tty.legacy_tiocsti=1" >> /etc/sysctl.conf\n'
            message += "More details about this bug here: https://github.com/Orange-Cyberdefense/arsenal/issues/77"
            print(message)
        # restore TTY attribute for stdin
        termios.tcsetattr(stdin, termios.TCSADRAIN, oldattr)

def main():
    if not os.path.exists(config.CONFIG_PATH):
        copy(config.DEFAULT_CONFIG_PATH, config.CONFIG_PATH)
    try:
        ArsenalNG().run()
    except KeyboardInterrupt:
        exit(0)


if __name__ == "__main__":
    wrapper(main()) 
