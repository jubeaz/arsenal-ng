from textual.widgets import Input, TextArea
from textual.containers import Container, VerticalScroll
from textual import events, on
import glob
from os.path import isdir
from os import sep

from arsenalng.data import config
from arsenalng.models.command import Command
from arsenalng.gui.modals.mouselessmodal import MouselessModal


class CmdEditModal(MouselessModal):
    cmd = None
    infobox = None
    focus_save = None

    def __init__(self, cheat, arsenalng_global_vars, name=None, id=None, classes=None):
        self.infobox = TextArea.code_editor(id="cmdeditModal_infobox", text="")
        self.infobox.cursor_blink = False
        self.infobox.read_only = True
        self.inputs = {}
        self.cmd = Command(cheat, arsenalng_global_vars)
        super().__init__(name=name, id=id, classes=classes)

    def compose(self):
        with Container():
            yield self.infobox
            with VerticalScroll():
                for arg_name, arg_data in self.cmd.args.items():
                    self.inputs[arg_name] = Input(id=arg_name, placeholder="", type="text", value=arg_data["value"])
                    yield self.inputs[arg_name]
                    self.inputs[arg_name].border_title = arg_name
        self.infobox.load_text(self.cmd.preview())

    def on_mount(self) -> None:
        if len(self.inputs):
            self.set_focus(self.inputs[next(iter(self.inputs.keys()))])
            self.focus_save = self.focused

    @on(Input.Changed)
    def recompute_table(self, event: Input.Changed):
        for name, i in self.inputs.items():
            value = i.value if i.value is not None else ""
            self.cmd.set_arg(name, value)
        self.infobox.load_text(self.cmd.preview())

    def on_key(self, event: events.Key) -> None:
        event.stop()
        if event.key in ["tab", "down", "shift+tab", "up"]:
            if event.key == "tab":
                if self.focused.value is None:
                    self.focus_next()
                else:
                    self.autocomplete_arg()
                    self.focused.action_end()
            elif event.key == "down":
                self.focus_next()
                if self.focused == self.infobox:
                    self.focus_next()
            elif event.key == "shift+tab" or event.key == "up":
                self.focus_previous()
                if self.focused == self.infobox:
                    self.focus_previous()
            self.focus_save = self.focused
            self.query_one(VerticalScroll).scroll_to_widget(self.focused)
        elif event.key == "ctrl+t":
            try:
                from pyfzf.pyfzf import FzfPrompt
                files = []
                for fuzz_dir in config.FUZZING_DIRS:
                    files += glob.glob(fuzz_dir, recursive=True)
                fzf = FzfPrompt().prompt(files)
                self.focused.value = fzf[0]
            except ImportError:
                pass
        elif event.key == "left":
            self.focused.action_cursor_left()
        elif event.key == "right":
            self.focused.action_cursor_right()
        elif event.key == "backspace":
            self.focused.action_delete_left()
        elif event.key == "delete":
            self.focused.action_delete_right()
        elif event.key == "home":
            self.focused.action_home()
        elif event.key == "end":
            self.focused.action_end()
        elif event.key == "enter":
            for name, i in self.inputs.items():
                value = i.value if i.value is not None else ""
                self.cmd.set_arg(name, value)
            if self.cmd.build():
                self.dismiss(self.cmd.cmdline)
        elif event.key == "escape":
            self.dismiss(None)


    def autocomplete_arg(self):
        """Autocomplete the current argument"""
        # current argument value
        # look for all files that match the argument in the working directory
        matches = glob.glob(f"{self.focused.value}*")

        if not matches:
            return False

        # init the autocompleted argument
        autocompleted_argument = ""
        # autocompleted argument is the longest start common string in all matches
        for i in range(len(min(matches))):
            if not all(min(matches)[:i + 1] == match[:i + 1] for match in matches):
                break
            autocompleted_argument = min(matches)[:i + 1]

        # add a "/" at the end of the autocompleted argument if it is a directory
        if isdir(autocompleted_argument) and autocompleted_argument[-1] != sep:
            autocompleted_argument = autocompleted_argument + sep

        # autocomplete the argument 
        self.focused.value = autocompleted_argument