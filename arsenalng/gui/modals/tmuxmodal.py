from textual.widgets import Label, ListView
from textual.containers import Horizontal, Vertical
from textual.widgets import Button
from textual import events
import libtmux
import random
import string
import time

from arsenalng.gui.modals.mouselessmodal import MouselessModal
from arsenalng.gui.widgets.mouselesslistview import MouselessListView
from arsenalng.gui.widgets.mouselesslabelitem import MouselessLabelItem

class TmuxModal(MouselessModal):
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
        with Vertical( ):
            with Horizontal(id="tmuxmodal_horizontal_top"):
                yield Label("",id="tmuxmodal_session_chosen")
                yield Label("",id="tmuxmodal_window_chosen")
                yield Label("",id="tmuxmodal_pane_chosen")
                #yield self.w_pane_in
            with Horizontal(id="tmuxmodal_horizontal_middle"):
                yield MouselessListView(id="tmuxmodal_session_li")
                yield MouselessListView(id="tmuxmodal_window_li")
                yield MouselessListView(id="tmuxmodal_pane_li")
                #yield self.w_pane_in
            with Horizontal(id="tmuxmodal_horizontal_bottom"):    
                yield self.w_ok_bt
                yield Label("prefix-q", id="tmuxmodal_tmux_pane_cmd")


    def on_mount(self) -> None:
        self.w_session_li = self.query_one("#tmuxmodal_session_li")
        self.w_session_li.border_title = "Sessions"
        self.w_window_li = self.query_one("#tmuxmodal_window_li")
        self.w_window_li.border_title = "Windows"
        self.w_pane_li = self.query_one("#tmuxmodal_pane_li")
        self.w_pane_li.border_title = "Panes"
        for s in self.tmux_server.sessions:
            self.w_session_li.append(MouselessLabelItem(s.name))  # Label and value can both be the string
        self.set_focus(self.w_session_li)
        self.focus_save = self.focused

    def on_key(self, event: events.Key) -> None:
        event.stop()
        if event.key == "escape":
            self.dismiss()
        elif self.focused == self.w_session_li or self.focused == self.w_window_li or self.focused == self.w_pane_li:
            self.listview_on_key(event)
        elif self.focused == self.w_ok_bt:
            self.button_on_key(event)

    def button_on_key(self, event: events.Key) -> None:
        if event.key == "right" or event.key == "tab":
            self.focus_next()
            self.focus_save = self.focused
        elif event.key == "left" or event.key == "shift+tab":
            self.focus_previous()
            self.focus_save = self.focused
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
            self.focus_save = self.focused
        elif event.key == "left" or event.key == "shift+tab":
            self.focus_previous()
            self.focus_save = self.focused
        elif event.key == "up":
            self.focused.action_cursor_up()
        elif event.key == "down":
            self.focused.action_cursor_down()
        return

    def on_list_view_selected(self, event: ListView.Selected):
        if event.control.id == "tmuxmodal_session_li":
            self.tmux_session_name = event.item.label
            self.tmux_window_name = ""
            self.tmux_window = None
            self.tmux_pane_indx = ""
            self.tmux_pane = None
            self.select_tmux_session()
        elif event.control.id == "tmuxmodal_window_li":
            self.tmux_window_name = event.item.label
            self.tmux_pane_indx = ""
            self.tmux_pane = None
            self.select_tmux_window()
        elif event.control.id == "tmuxmodal_pane_li":
            self.tmux_pane_indx = event.item.label
            self.select_tmux_pane()
        self.query_one("#tmuxmodal_session_chosen",Label).update(self.tmux_session_name)
        self.query_one("#tmuxmodal_window_chosen",Label).update(self.tmux_window_name)
        self.query_one("#tmuxmodal_pane_chosen",Label).update(self.tmux_pane_indx)

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
                self.w_pane_li.append(MouselessLabelItem(p.index))  # Label and value can both be the string
            self.w_pane_li.append(MouselessLabelItem("<all_panes>"))
        self.w_pane_li.append(MouselessLabelItem("<new_pane>"))


    def select_tmux_session(self):
        self.w_window_li.clear()
        try:
            self.tmux_session = self.tmux_server.sessions.get(session_name=self.tmux_session_name)
        except libtmux._internal.query_list.ObjectDoesNotExist:
            raise RuntimeError(f"Could not find session {self.arsenalng_global_vars["arsenalng_tmux_session_name"]}") from None 

        for w in self.tmux_session.windows:
            self.w_window_li.append(MouselessLabelItem(w.name))  # Label and value can both be the string
        self.w_window_li.append(MouselessLabelItem("<new_window>"))

