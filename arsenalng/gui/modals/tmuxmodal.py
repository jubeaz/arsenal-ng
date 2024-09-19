from textual.screen import ModalScreen
from textual.widgets import Label, ListView, Footer
from textual.containers import Horizontal, Vertical
from textual.widgets import Button
from textual import events
import libtmux
import random
import string
import time

from arsenalng.gui.widgets.arsenalnglistview import ArsenalNGListView, LabelItem


class TmuxModal(ModalScreen[str]):
    arsenalng_global_vars = None
    tmux_server = None
    tmux_session = None
    tmux_session_name = ""
    tmux_window = None
    tmux_window_name = ""
    is_tmux_new_window = False
    tmux_pane = None
    tmux_pane_indx = ""

    w_session_li = None
    w_window_li = None
    w_pane_li = None
    w_ok_bt = None
    focus_save = None

    def __init__(self, arsenalng_global_vars, tmux_server, name=None, id=None, classes=None):
        self.arsenalng_global_vars = arsenalng_global_vars
        self.tmux_server = tmux_server
        self.tmux_session_name = ""
        self.tmux_window_name = ""
        self.tmux_pane_indx = ""
        assert self.tmux_server.is_alive()
        super().__init__(name=name, id=id, classes=classes)

    def compose(self):
        self.w_ok_bt = Button("OK")
        #self.w_pane_in = Input(id="arsenalng_tmux_pane_id", placeholder="pane_id", type="text", value=self.arsenalng_global_vars["arsenalng_tmux_pane_id"])
        with Vertical( ):
            with Horizontal(id="tmuxmodal_horizontal_top"):
                yield Label("",id="session_chosen")
                yield Label("",id="window_chosen")
                yield Label("",id="pane_chosen")
                #yield self.w_pane_in
            with Horizontal(id="tmuxmodal_horizontal_middle"):
                yield ArsenalNGListView(id="session_li")
                yield ArsenalNGListView(id="window_li")
                yield ArsenalNGListView(id="pane_li")
                #yield self.w_pane_in
            with Horizontal(id="tmuxmodal_horizontal_bottom"):    
                yield self.w_ok_bt
                yield Label("prefix-q", id="tmux_pane_cmd")


    def on_mount(self) -> None:
        self.w_session_li = self.query_one("#session_li")
        self.w_window_li = self.query_one("#window_li")
        self.w_pane_li = self.query_one("#pane_li")
        for s in self.tmux_server.sessions:
            self.w_session_li.append(LabelItem(s.name))  # Label and value can both be the string
        self.set_focus(self.w_session_li)
        self.focus_save = self.focused

    def on_click(self, event: events.Click) -> None:
        """Prevent click"""
        event.prevent_default()
        event.stop()
        return

    def on_mouse_down(self, event: events.MouseDown) -> None:
        """Prevent click"""
        event.prevent_default()
        event.stop()
        self.set_focus(self.focus_save)
        return

    def on_mouse_up(self, event: events.MouseUp) -> None:
        """Prevent click"""
        event.prevent_default()
        event.stop()
        self.set_focus(self.focus_save)
        return

    def on_key(self, event: events.Key) -> None:
        event.stop()
        if event.key == "escape":
            self.dismiss()
        #elif self.focused == self.w_pane_in:
        #    self.input_on_key(event)
        elif self.focused == self.w_session_li or self.focused == self.w_window_li or self.focused == self.w_pane_li:
            self.listview_on_key(event)
        elif self.focused == self.w_ok_bt:
            self.button_on_key(event)

    def input_on_key(self, event: events.Key) -> None:
        if event.key in ["tab", "shift+tab"]:
            if event.key == "tab":
                    self.focus_next()
            elif event.key == "shift+tab":
                self.focus_previous()
            self.focus_save = self.focused
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

    def button_on_key(self, event: events.Key) -> None:
        if event.key == "right" or event.key == "tab":
            self.focus_next()
        elif event.key == "left" or event.key == "shift+tab":
            self.focus_previous()
        elif event.key == "enter" and self.tmux_session_name != "" and self.tmux_window_name != "":
            if self.tmux_window_name == "<new_window>":
                self.tmux_window_name = "".join(random.choices(string.ascii_letters + string.digits, k=16))
            self.build_tmux()
            result = {}
            result["arsenalng_tmux_session_name"] = self.tmux_session_name
            result["tmux_session"] = self.tmux_session
            result["arsenalng_tmux_window_name"] = self.tmux_window_name
            result["tmux_window"] = self.tmux_window
            result["arsenalng_tmux_pane_indx"] = self.tmux_pane_indx
            result["tmux_pane"] = self.tmux_pane

            self.dismiss(result)


    def listview_on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            self.focused.action_select_cursor()
        elif event.key == "right" or event.key == "tab":
            self.focus_next()
        elif event.key == "left" or event.key == "shift+tab":
            self.focus_previous()
        elif event.key == "up":
            self.focused.action_cursor_up()
        elif event.key == "down":
            self.focused.action_cursor_down()
        return

    def on_list_view_selected(self, event: ListView.Selected):
        if event.control.id == "session_li":
            self.tmux_session_name = event.item.label
            self.tmux_window_name = ""
            self.tmux_window = None
            self.tmux_pane_indx = ""
            self.tmux_pane = None
            self.select_tmux_session()
        elif event.control.id == "window_li":
            self.tmux_window_name = event.item.label
            self.tmux_pane_indx = ""
            self.tmux_pane = None
            self.select_tmux_window()
        elif event.control.id == "pane_li":
            self.tmux_pane_indx = event.item.label
            self.select_tmux_pane()
        self.query_one("#session_chosen",Label).update(self.tmux_session_name)
        self.query_one("#window_chosen",Label).update(self.tmux_window_name)
        self.query_one("#pane_chosen",Label).update(self.tmux_pane_indx)

        return

    def build_tmux(self):
        if self.is_tmux_new_window:
            self.tmux_window = self.tmux_session.new_window(attach=False, window_name=self.tmux_window_name)
            self.tmux_pane = self.tmux_window.panes[0]
            self.tmux_pane_indx = 0
        elif self.tmux_pane_indx == "<new_pane>":
            self.tmux_pane_indx = len(self.tmux_window.panes) + 1
            self.tmux_pane = self.tmux_window.split_window(attach=False)
            time.sleep(0.3)
        elif self.tmux_pane_indx == "<all_panes>": 
            self.tmux_pane_indx = None
            self.tmux_pane = None
        else:
            self.tmux_pane_indx = int(self.tmux_pane_indx)
            self.tmux_pane = self.tmux_window.panes[self.tmux_pane_indx]

    def select_tmux_pane(self):
        if self.is_tmux_new_window:
            self.tmux_pane_indx = "0"


    def select_tmux_window(self):
        self.is_tmux_new_window = False
        self.w_pane_li.clear()
        try:
            self.tmux_window = self.tmux_session.select_window(self.tmux_window_name)
        except libtmux.exc.LibTmuxException:
            self.is_tmux_new_window = True
        if self.is_tmux_new_window is False:
            for p in self.tmux_window.panes:
                self.w_pane_li.append(LabelItem(p.index))  # Label and value can both be the string
            self.w_pane_li.append(LabelItem("<all_panes>"))
        self.w_pane_li.append(LabelItem("<new_pane>"))


    def select_tmux_session(self):
        self.w_window_li.clear()
        try:
            self.tmux_session = self.tmux_server.sessions.get(session_name=self.tmux_session_name)
        except libtmux._internal.query_list.ObjectDoesNotExist:
            raise RuntimeError(f"Could not find session {self.arsenalng_global_vars["arsenalng_tmux_session_name"]}") from None 

        for w in self.tmux_session.windows:
            self.w_window_li.append(LabelItem(w.name))  # Label and value can both be the string
        self.w_window_li.append(LabelItem("<new_window>"))

