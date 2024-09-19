from textual.app import App, ComposeResult
from textual.widgets import Label, Input, TextArea
from textual.containers import Container
from textual import events, on
from os.path import exists
import json
import math
import time
import re
import libtmux

from arsenalng.data import config
from arsenalng.gui.widgets.cheasdatatable import CheatsDataTable
from arsenalng.gui.modals.argseditmodal import ArgsEditModal
from arsenalng.gui.modals.globalvarsmodal import GlobalVarsModal
from arsenalng.gui.modals.tmuxmodal import TmuxModal




class FakeCommand:
    def __init__(self, cmdline):
        self.cmdline = cmdline

            
class ArsenalNGGui(App):
    CSS_PATH = "gui.tcss"
    AUTO_FOCUS = "Input"
    global_cheats = []  # all cheats
    filtered_cheats = []  # cheats after search
    input_buffer = ""
    cmd = ""
    args = None
    arsenalng_global_vars = dict()
    tmux_session = None
    tmux_server = None

    arg_edit_modal = None
    global_vars_modal = None
    tmux_modal = None
    
    w_cheats_dt = None
    w_search_input = None
    w_cmd_preview = None

    def __init__(self, driver_class=None, css_path=None, watch_css=False, cheatsheets=None, args=None, tmux_session=None):
        super().__init__(driver_class=None, css_path=None, watch_css=False)
        self.args = args
        self.tmux_session = tmux_session
        self.tmux_server = None
        self.arg_edit_modal = None
        self.global_vars_modal = None
        self.tmux_modal = None
        for value in cheatsheets.values():
            self.global_cheats.append(value)
        self.load_arsenalng_global_vars()
        self.filtered_cheats = self.filter_cheats()

    def load_arsenalng_global_vars(self):
        if exists(config.savevarfile):
            with open(config.savevarfile) as f:
                self.arsenalng_global_vars = json.load(f)

    def save_arsenalng_global_vars(self):
        with open(config.savevarfile, "w") as f:
            f.write(json.dumps(self.arsenalng_global_vars))

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        self.cursor_blink = False

        self.w_cmd_preview = TextArea.code_editor(id="infobox", text="")
        self.w_cmd_preview.cursor_blink = False
        self.w_cmd_preview.read_only = True

        self.w_cheats_dt = CheatsDataTable(id="table")
        self.w_cheats_dt.cursor_type = "row"
        self.w_cheats_dt.zebra_stripes = True

        self.w_search_input = Input(id="search", placeholder="Search", type="text")

        yield self.w_cmd_preview
        yield self.w_search_input
        yield Container(self.w_cheats_dt)
        # A VOIR CE QUE L'ON FAIT ICI
        yield Label("count")


    def on_mount(self) -> None:
        win_width = self.size.width
        prompt = "> "
        max_width = win_width - len(prompt) - len("\n")
        self.col2_size = math.floor(max_width * 14 / 100)
        self.col1_size = math.floor(max_width * 8 / 100)
        self.col3_size = math.floor(max_width * 23 / 100)
        self.col4_size = math.floor(max_width * 55 / 100)
        self.compute_w_cheats_dt()
        self.set_focus(self.w_search_input)

    def on_mouse_down(self) -> None:
        """Reset focus on w_search_input"""
        self.set_focus(self.w_search_input)

    def action_focus_previous(self):
        return

    def action_focus_next(self):
        return

    @on(Input.Changed)
    def recompute_w_cheats_dt(self, event: Input.Changed):
        self.input_buffer = self.w_search_input.value
        self.w_cheats_dt.clear(columns=True)
        self.compute_w_cheats_dt()

    def on_key(self, event: events.Key) -> None:
        def display_global_vars(resut: str) -> None:
            """Called when QuitScreen is dismissed."""
            self.global_vars_modal = None

        def check_cmd(cmdline: str) -> None:
            """Called when QuitScreen is dismissed."""
            if cmdline:
                self.process_cmdline(cmdline)
            else:
                self.arg_edit_modal.cmd = None
                self.arg_edit_modal = None
 
        # https://github.com/Textualize/textual/blob/main/src/textual/keys.py
        if event.key == "down":
            r = self.w_cheats_dt.cursor_row
            self.w_cheats_dt.move_cursor(row=r + 1)
            self.w_cmd_preview.load_text(f"{self.filtered_cheats[self.w_cheats_dt.cursor_row].name} \n {self.filtered_cheats[self.w_cheats_dt.cursor_row].printable_command}")
            
        elif event.key == "up":
            r = self.w_cheats_dt.cursor_row
            self.w_cheats_dt.move_cursor(row=r - 1)
            self.w_cmd_preview.load_text(f"{self.filtered_cheats[self.w_cheats_dt.cursor_row].name} \n {self.filtered_cheats[self.w_cheats_dt.cursor_row].printable_command}")

        elif event.key == "pageup":
            self.w_cheats_dt.action_page_up()
            self.w_cmd_preview.load_text(f"{self.filtered_cheats[self.w_cheats_dt.cursor_row].name} \n {self.filtered_cheats[self.w_cheats_dt.cursor_row].printable_command}")

        elif event.key == "pagedown":
            self.w_cheats_dt.action_page_down()
            self.w_cmd_preview.load_text(f"{self.filtered_cheats[self.w_cheats_dt.cursor_row].name} \n {self.filtered_cheats[self.w_cheats_dt.cursor_row].printable_command}")

        elif event.key == "enter":
            if self.filtered_cheats[self.w_cheats_dt.cursor_row].command == ">exit":
                self.exit()
            elif self.filtered_cheats[self.w_cheats_dt.cursor_row].command == ">clear":
                self.arsenalng_global_vars = dict()
            elif self.filtered_cheats[self.w_cheats_dt.cursor_row].command == ">reload":
                self.load_arsenalng_global_vars()
            elif self.filtered_cheats[self.w_cheats_dt.cursor_row].command == ">save":
                self.save_arsenalng_global_vars()
            elif self.filtered_cheats[self.w_cheats_dt.cursor_row].command == ">show":
                self.global_vars_modal = GlobalVarsModal(self.arsenalng_global_vars)
                self.push_screen(self.global_vars_modal, display_global_vars)
            else:
                self.arg_edit_modal = ArgsEditModal(self.filtered_cheats[self.w_cheats_dt.cursor_row], self.arsenalng_global_vars)
                self.push_screen(self.arg_edit_modal, check_cmd)

        elif event.key == "escape":
            self.exit()      


    def filter_cheats(self):
        """
        Return the list of cheatsheet who match the searched term
        :return: list of cheatsheet to show
        """
        return list(filter(self.match, self.global_cheats)) if self.input_buffer != "" else self.global_cheats

    def compute_w_cheats_dt(self):
        self.filtered_cheats = self.filter_cheats()
        self.w_cheats_dt.add_column("tags", width=self.col1_size)
        self.w_cheats_dt.add_column("title", width=self.col2_size)
        self.w_cheats_dt.add_column("name", width=self.col3_size)
        self.w_cheats_dt.add_column("command", width=self.col4_size)
        for i, cheat in enumerate(self.filtered_cheats):
            tags = cheat.get_tags()
            self.w_cheats_dt.add_row(tags, cheat.str_title, cheat.name, cheat.printable_command, key=i)

    def match(self, cheat):
        """
        Function called by the iterator to verify if the cheatsheet match the entered values
        :param cheat: cheat to check
        :return: boolean
        """
        # if search begin with '>' print only internal CMD
        if self.input_buffer.startswith(">") and not cheat.command.startswith(">"):
            return False

        for value in self.input_buffer.lower().split(" "):
            is_value_excluded = False
            if value.startswith("!") and len(value) > 1:
                value = value[1:]
                is_value_excluded = True

            if (value in cheat.str_title.lower()
                    or value in cheat.name.lower()
                    or value in cheat.tags.lower()
                    or value in "".join(cheat.command_tags.values()).lower()
                    or value in cheat.command.lower()):
                if is_value_excluded:
                    return False

            elif not is_value_excluded:
                return False
        return True

    def is_main_screen_active(self):
        return self.arg_edit_modal is None

    def process_cmdline(self, cmdline):
        """Function that process the cmdline generated"""
        if re.match(r"^\>set( [^= ]+=[^= ]+)+$", cmdline):
            # Add new glovar var
            varlist = re.findall("([^= ]+)=([^= ]+)", cmdline)
            for v in varlist:
                self.arsenalng_global_vars[v[0]] = v[1]
            return    
        if self.args.prefix:
                cmdline = self.prefix_cmdline_with_prefix(cmdline)

        if self.args.tmux is None:
            self.exit(result=FakeCommand(cmdline))
        else:
            self.process_tmux(cmdline)

    def prefix_cmdline_with_prefix(self, cmdline):
        if config.PREFIX_GLOBALVAR_NAME in self.arsenalng_global_vars:
            cmdline = f"{self.arsenalng_global_vars[config.PREFIX_GLOBALVAR_NAME]} {cmdline}"
        return cmdline

    def process_tmux(self, cmdline):
        def validate_tmux_modal(resut: str) -> None:
            self.tmux_modal = None
            if not resut: # user cancel
                return
            # set back global vars
            self.arsenalng_global_vars["arsenalng_tmux_session_name"] = resut["arsenalng_tmux_session_name"]
            self.arsenalng_global_vars["arsenalng_tmux_window_name"] = resut["arsenalng_tmux_window_name"]
            self.arsenalng_global_vars["arsenalng_tmux_pane_id"] = resut["arsenalng_tmux_pane_id"]
            # if there error relaunch modal 
            if self.tmux_server is None:
                self.tmux_server = libtmux.Server()
            try:
                self.tmux_session = self.tmux_server.sessions.get(session_name=self.arsenalng_global_vars["arsenalng_tmux_session_name"])
            except libtmux._internal.query_list.ObjectDoesNotExist:
                raise RuntimeError(f"Could not find session {self.arsenalng_global_vars["arsenalng_tmux_session_name"]}") from None 
            new_window = False
            try:
                window = self.tmux_session.select_window(self.arsenalng_global_vars["arsenalng_tmux_window_name"])
            except libtmux.exc.LibTmuxException:
                window = self.tmux_session.new_window(attach=False, window_name=self.arsenalng_global_vars["arsenalng_tmux_window_name"])
                new_window = True
            if new_window:
                pane = window.panes[0] 
            elif self.arsenalng_global_vars["arsenalng_tmux_pane_id"] == "": # all panes
                pane = None
            elif int(self.arsenalng_global_vars["arsenalng_tmux_pane_id"]) > len(window.panes):
                pane = window.split_window(attach=False)
                time.sleep(0.3)
            else:
                pane = window.panes[int(self.arsenalng_global_vars["arsenalng_tmux_pane_id"])]
            if pane:
                if self.args.exec:
                    pane.send_keys(cmdline)
                else:
                    pane.send_keys(cmdline, enter=False)
                    pane.select_pane()
            else:
                for pane in window.panes:
                    if self.args.exec:
                        pane.send_keys(cmdline)
                    else:
                        pane.send_keys(cmdline, enter=False)
                        pane.select_pane()


        # assert tmux global var
        if "arsenalng_tmux_session_name" not in self.arsenalng_global_vars:
            self.arsenalng_global_vars["arsenalng_tmux_session_name"] = ""
        if "arsenalng_tmux_window_name" not in self.arsenalng_global_vars:
            self.arsenalng_global_vars["arsenalng_tmux_window_name"] = ""
        if "arsenalng_tmux_pane_id" not in self.arsenalng_global_vars:
            self.arsenalng_global_vars["arsenalng_tmux_pane_id"] = ""
        self.tmux_modal = TmuxModal(self.arsenalng_global_vars)
        self.push_screen(self.tmux_modal, validate_tmux_modal)


