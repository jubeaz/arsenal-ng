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
from arsenalng.gui.modals.helpmodal import HelpModal
       
class ArsenalNGGui(App):
    CSS_PATH = "gui.tcss"
    AUTO_FOCUS = "Input"
    global_cheats = []  # all cheats
    filtered_cheats = []  # cheats after search
    input_buffer = ""
    cmdline = ""
    args = None
    arsenalng_global_vars = {}

    tmux_session = None
    tmux_server = None

    arg_edit_modal = None
    global_vars_modal = None
    tmux_modal = None
    help_modal = None
    
    w_cheats_dt = None
    w_search_input = None
    w_cmd_preview = None

    def __init__(self, driver_class=None, css_path=None, watch_css=False, cheatsheets=None, args=None):
        super().__init__(driver_class=None, css_path=None, watch_css=False)
        self.args = args
        self.cmdline = ""

        self.tmux_session = None
        if self.args.tmux is not None:
            self.tmux_server_connect()
        else:   
            self.tmux_server = None
        
        self.arg_edit_modal = None
        self.global_vars_modal = None
        self.tmux_modal = None
        self.help_modal = HelpModal()

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
        elif event.key == "f1":
            self.push_screen(self.help_modal)
        elif event.key == "f2":
            self.global_vars_modal = GlobalVarsModal(self.arsenalng_global_vars)
            self.push_screen(self.global_vars_modal, self.global_vars_callback)
        elif event.key == "f3":
            self.load_arsenalng_global_vars()
        elif event.key == "f4":
            self.save_arsenalng_global_vars()
        elif event.key == "f5":
            self.arsenalng_global_vars = {}           
        elif event.key == "enter":
            self.arg_edit_modal = ArgsEditModal(self.filtered_cheats[self.w_cheats_dt.cursor_row], self.arsenalng_global_vars)
            self.push_screen(self.arg_edit_modal, self.arg_edit_callback)

        elif event.key == "escape":
            self.exit()      

    def compute_w_cheats_dt(self):
        self.filtered_cheats = self.filter_cheats()
        self.w_cheats_dt.add_column("tags", width=self.col1_size)
        self.w_cheats_dt.add_column("title", width=self.col2_size)
        self.w_cheats_dt.add_column("name", width=self.col3_size)
        self.w_cheats_dt.add_column("command", width=self.col4_size)
        for i, cheat in enumerate(self.filtered_cheats):
            tags = cheat.get_tags()
            self.w_cheats_dt.add_row(tags, cheat.str_title, cheat.name, cheat.printable_command, key=i)

    def filter_cheats(self):
        """
        Return the list of cheatsheet who match the searched term
        :return: list of cheatsheet to show
        """
        return list(filter(self.filter_cheats_match, self.global_cheats)) if self.input_buffer != "" else self.global_cheats

    def filter_cheats_match(self, cheat):
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

    def process_internal_cmdline(self):
        """Function that process the internal cmdline generated"""
        if re.match(r"^\>set( [^= ]+=[^= ]+)+$", self.cmdline):
            # Add new glovar var
            varlist = re.findall("([^= ]+)=([^= ]+)", self.cmdline)
            for v in varlist:
                self.arsenalng_global_vars[v[0]] = v[1]
            return

    def process_cmdline(self):
        """Function that process the cmdline generated"""
        if self.args.prefix:
            self.prefix_cmdline_with_prefix(self.cmdline)

        if self.args.tmux is None:
            self.exit(self.cmdline)
        else:
            self.process_tmux()

    def prefix_cmdline_with_prefix(self, cmdline):
        if config.PREFIX_GLOBALVAR_NAME in self.arsenalng_global_vars:
            self.cmdline = f"{self.arsenalng_global_vars[config.PREFIX_GLOBALVAR_NAME]} {cmdline}"

    def process_tmux(self):
        # assert tmux global var
        if "arsenalng_tmux_session_name" not in self.arsenalng_global_vars:
            self.arsenalng_global_vars["arsenalng_tmux_session_name"] = ""
        if "arsenalng_tmux_window_name" not in self.arsenalng_global_vars:
            self.arsenalng_global_vars["arsenalng_tmux_window_name"] = ""
        if "arsenalng_tmux_pane_id" not in self.arsenalng_global_vars:
            self.arsenalng_global_vars["arsenalng_tmux_pane_id"] = ""
        self.tmux_modal = TmuxModal(self.arsenalng_global_vars, self.tmux_server)
        self.push_screen(self.tmux_modal, self.tmux_callback)

    def tmux_server_connect(self) -> None:
        if self.tmux_server is None:
            self.tmux_server = libtmux.Server()
        assert self.tmux_server.is_alive()


    def tmux_callback(self, result) -> None:
        self.tmux_modal = None
        if not result: # user cancel
            return
        # set back global vars
        self.arsenalng_global_vars["arsenalng_tmux_session_name"] = result["arsenalng_tmux_session_name"]
        self.arsenalng_global_vars["arsenalng_tmux_window_name"] = result["arsenalng_tmux_window_name"]
        self.arsenalng_global_vars["arsenalng_tmux_pane_indx"] = result["arsenalng_tmux_pane_indx"]
        if result["tmux_pane"]:
            if self.args.exec:
                result["tmux_pane"].send_keys(self.cmdline)
            else:
                result["tmux_pane"].send_keys(self.cmdline, enter=False)
                result["tmux_pane"].select_pane()
        else:
            for pane in result["tmux_window"].panes:
                if self.args.exec:
                    pane.send_keys(self.cmdline)
                else:
                    pane.send_keys(self.cmdline, enter=False)
                    pane.select_pane()

    def global_vars_callback(self, resut: str) -> None:
        """Called when QuitScreen is dismissed."""
        self.global_vars_modal = None

    def arg_edit_callback(self, cmdline: str) -> None:
        """Called when QuitScreen is dismissed."""
        self.cmdline = cmdline
        
        if cmdline is None:
            self.arg_edit_modal.cmd = None
            self.arg_edit_modal = None
            return
        if self.cmdline[0] == ">":
            self.process_internal_cmdline()
        else:
            self.process_cmdline()

