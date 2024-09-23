from textual.app import App, ComposeResult
from textual.widgets import Label, Input, Footer
from textual.binding import Binding
from textual.containers import Container
from textual import events, on
from os.path import exists
import json
import math
import re
import libtmux

from arsenalng.data import config
from arsenalng.models.tmuxmanager import TmuxManager
from arsenalng.gui.widgets.mouselessdatatable import MouselessDataTable
from arsenalng.gui.modals.cmdeditmodal import CmdEditModal
from arsenalng.gui.modals.globalvarsmodal import GlobalVarsModal
from arsenalng.gui.modals.globalvarseditmodal import GlobalVarsEditModal
from arsenalng.gui.modals.tmuxmodal import TmuxModal
from arsenalng.gui.modals.cheatpreviewmodal import CheatPreviewModal
       
class ArsenalNGGui(App):
    BINDINGS = [
        Binding(key="f1", action="edit_global_vars", description="Edit GlobalVars"),
        Binding(key="f2", action="show_global_vars", description="Show GlobalVars"),
        Binding(key="f3", action="load_global_vars", description="Reload"),
        Binding(key="f4", action="save_global_vars", description="Save"),
        Binding(key="f5", action="clear_global_vars", description="clear"),
        Binding(key="escape", action="quit", description="quit"),
        Binding(key="down", action="next", description="Next", show=True),
        Binding(key="up", action="prev", description="Prev", show=True),
        Binding(key="pageup", action="page_up", description="PG Up", show=True),
        Binding(key="pagedown", action="page_down", description="PG Down", show=True),
        Binding(key="enter", action="cheat_edit", description="Edit", show=True),
        Binding(key="tab", action="cheat_preview", description="Preview", show=True),
    ]

    CSS_PATH = "gui.tcss"
    AUTO_FOCUS = "Input"
    global_cheats = []  # all cheats
    filtered_cheats = []  # cheats after search
    input_buffer = ""
    cmdline = ""
    args = None
    arsenalng_global_vars = {}

    tmux_mgr = None

    cmd_edit_modal = None
    global_vars_modal = None
    tmux_modal = None
    cheat_preview_modal = None
    
    w_cheats_dt = None
    w_search_input = None
    w_cmd_preview = None

    focus_save = None

    def __init__(self, driver_class=None, css_path=None, watch_css=False, cheatsheets=None, args=None):
        super().__init__(driver_class=None, css_path=None, watch_css=False)
        self.args = args
        self.cmdline = ""

        self.tmux_session = None
        if self.args.tmux is not None:
            self.tmux_mgr = TmuxManager(libtmux.Server())
        else:   
            self.tmux_mgr = None
        
        self.cmd_edit_modal = None
        self.global_vars_modal = None
        self.tmux_modal = None

        for value in cheatsheets.values():
            self.global_cheats.append(value)

        self.action_load_global_vars()
        self.filtered_cheats = self.filter_cheats()

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        self.cursor_blink = False
        self.w_cmd_preview = Label("", id="guing_infobox")
        self.w_cmd_preview.border_title = ""

        self.w_cheats_dt = MouselessDataTable(id="guing_table")
        self.w_cheats_dt.cursor_type = "row"
        self.w_cheats_dt.zebra_stripes = False
        self.w_cheats_dt.border_title = "Commands"
        
        self.w_search_input = Input(id="guing_search", placeholder="Search", type="text")
        self.w_search_input.border_title = "Search"
        with Container():
            yield self.w_cmd_preview
            yield self.w_search_input
            yield self.w_cheats_dt
        yield Footer()

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
        self.focus_save = self.w_search_input

    def on_click(self, event: events.Click) -> None:
        """Prevent Click"""
        event.prevent_default()
        event.stop()
        self.set_focus(self.focus_save)
        return

    def on_mouse_down(self, event: events.MouseDown) -> None:
        """Prevent MouseDown"""
        event.prevent_default()
        event.stop()
        self.set_focus(self.focus_save)
        return

    def on_mouse_up(self, event: events.MouseUp) -> None:
        """Prevent MouseUp"""
        event.prevent_default()
        event.stop()
        self.set_focus(self.focus_save)
        return

    def on_mouse_scroll_down(self, event: events.MouseScrollDown) -> None:
        """Prevent MouseScrollDown"""
        event.prevent_default()
        event.stop()
        return

    def on_mouse_scroll_up(self, event: events.MouseScrollUp) -> None:
        """Prevent MouseScrollUp"""
        event.prevent_default()
        event.stop()
        return

    def on_mouse_capture(self, event: events.MouseCapture) -> None:
        """Prevent MouseCapture"""
        event.prevent_default()
        event.stop()
        return 
    def on_mouse_event(self, event: events.MouseEvent) -> None:
        """Prevent MouseEvent"""
        event.prevent_default()
        event.stop()
        return 
    def on_mouse_release(self, event: events.MouseRelease) -> None:
        """Prevent MouseReleasep"""
        event.prevent_default()
        event.stop()
        return 
 
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
        if event.key == "enter": # need here because enter catched by search input
            self.cmd_edit_modal = CmdEditModal(self.filtered_cheats[self.w_cheats_dt.cursor_row], self.arsenalng_global_vars)
            self.push_screen(self.cmd_edit_modal, self.arg_edit_callback)
        elif event.key == "tab":
            self.cheat_preveiw_modal = CheatPreviewModal(self.filtered_cheats[self.w_cheats_dt.cursor_row])
            self.push_screen(self.cheat_preveiw_modal)

    def action_quit(self):
            self.exit()      


    def action_edit_global_vars(self):
        self.global_vars_modal = GlobalVarsEditModal(self.arsenalng_global_vars)
        self.push_screen(self.global_vars_modal, self.edit_global_vars_callback) 

    def action_show_global_vars(self):
        self.global_vars_modal = GlobalVarsModal(self.arsenalng_global_vars)
        self.push_screen(self.global_vars_modal, self.global_vars_callback)

    def action_load_global_vars(self):
        if exists(config.savevarfile):
            with open(config.savevarfile) as f:
                self.arsenalng_global_vars = json.load(f)

    def action_save_global_vars(self):
        with open(config.savevarfile, "w") as f:
            f.write(json.dumps(self.arsenalng_global_vars, indent=4))

    def action_clear_global_vars(self):
        self.arsenalng_global_vars = {}

    def action_next(self):
        r = self.w_cheats_dt.cursor_row
        self.w_cheats_dt.move_cursor(row=r + 1)
        self.w_cmd_preview.update(f"{self.filtered_cheats[self.w_cheats_dt.cursor_row].printable_command}")
        self.w_cmd_preview.border_title = f"{self.filtered_cheats[self.w_cheats_dt.cursor_row].name}"

    def action_prev(self):
        r = self.w_cheats_dt.cursor_row
        self.w_cheats_dt.move_cursor(row=r - 1)
        self.w_cmd_preview.update(f"{self.filtered_cheats[self.w_cheats_dt.cursor_row].printable_command}")
        self.w_cmd_preview.border_title = f"{self.filtered_cheats[self.w_cheats_dt.cursor_row].name}"

    def action_page_up(self):
        self.w_cheats_dt.action_page_up()
        self.w_cmd_preview.update(f"{self.filtered_cheats[self.w_cheats_dt.cursor_row].printable_command}")
        self.w_cmd_preview.border_title = f"{self.filtered_cheats[self.w_cheats_dt.cursor_row].name}"

    def action_page_down(self):
        self.w_cheats_dt.action_page_down()
        self.w_cmd_preview.update(f"{self.filtered_cheats[self.w_cheats_dt.cursor_row].printable_command}")
        self.w_cmd_preview.border_title = f"{self.filtered_cheats[self.w_cheats_dt.cursor_row].name}"

    def action_cheat_edit(self):
        self.cmd_edit_modal = CmdEditModal(self.filtered_cheats[self.w_cheats_dt.cursor_row], self.arsenalng_global_vars)
        self.push_screen(self.cmd_edit_modal, self.arg_edit_callback)

    def action_cheat_preview(self):
        self.cheat_preveiw_modal = CheatPreviewModal(self.filtered_cheats[self.w_cheats_dt.cursor_row])
        self.push_screen(self.cheat_preveiw_modal)

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
        return self.cmd_edit_modal is None

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
        self.tmux_modal = TmuxModal(self.arsenalng_global_vars, self.tmux_mgr)
        self.push_screen(self.tmux_modal, self.tmux_callback)

    def tmux_callback(self, result) -> None:
        self.tmux_modal = None
        if not result: # user cancel
            return
        self.tmux_mgr = result
        # set back global vars
        self.arsenalng_global_vars["arsenalng_tmux_session_name"] = self.tmux_mgr.session_name
        self.arsenalng_global_vars["arsenalng_tmux_window_name"] = self.tmux_mgr.window_name
        self.arsenalng_global_vars["arsenalng_tmux_pane_indx"] = self.tmux_mgr.pane_indx
        if self.tmux_mgr.pane:
            if self.args.exec:
                self.tmux_mgr.pane.send_keys(self.cmdline)
            else:
                self.tmux_mgr.pane.send_keys(self.cmdline, enter=False)
                self.tmux_mgr.pane.select_pane()
        else:
            for pane in self.tmux_mgr.window.panes:
                if self.args.exec:
                    pane.send_keys(self.cmdline)
                else:
                    pane.send_keys(self.cmdline, enter=False)
                    pane.select_pane()

    def global_vars_callback(self, result) -> None:
        self.global_vars_modal = None

    def edit_global_vars_callback(self, result) -> None:
        self.global_vars_modal = None
        self.arsenalng_global_vars = result


    def arg_edit_callback(self, cmdline: str) -> None:
        """Called when QuitScreen is dismissed."""
        self.cmdline = cmdline
        
        if cmdline is None:
            self.cmd_edit_modal.cmd = None
            self.cmd_edit_modal = None
            return
        if self.cmdline[0] == ">":
            self.process_internal_cmdline()
        else:
            self.process_cmdline()

