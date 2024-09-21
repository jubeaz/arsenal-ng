from textual.widgets import Label, ListView
from textual.containers import Horizontal, Vertical
from textual.widgets import Button
from textual import events

from arsenalng.models.tmuxmanager import TmuxManager
from arsenalng.gui.modals.mouselessmodal import MouselessModal
from arsenalng.gui.widgets.mouselesslistview import MouselessListView
from arsenalng.gui.widgets.mouselesslabelitem import MouselessLabelItem

class TmuxModal(MouselessModal):
    arsenalng_global_vars = None
    tmux_mgr = None

    w_session_li = None
    w_window_li = None
    w_pane_li = None
    w_ok_bt = None
    focus_save = None

    def __init__(self, arsenalng_global_vars, tmux_mgr, name=None, id=None, classes=None):
        self.arsenalng_global_vars = arsenalng_global_vars
        self.tmux_mgr = tmux_mgr
        super().__init__(name=name, id=id, classes=classes)

    def compose(self):
        self.w_ok_bt = Button("Ok")
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

            yield self.w_ok_bt


    def on_mount(self) -> None:
        self.w_session_li = self.query_one("#tmuxmodal_session_li")
        self.w_session_li.border_title = "Session"
        self.w_window_li = self.query_one("#tmuxmodal_window_li")
        self.w_window_li.border_title = "Window"
        self.w_pane_li = self.query_one("#tmuxmodal_pane_li")
        self.w_pane_li.border_title = "Pane (pfx-q)"
        self.build_sessions()
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
        elif event.key == "enter" and self.tmux_mgr.is_finalizable():
            self.tmux_mgr.finalize()
            self.dismiss(self.tmux_mgr)

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
            self.w_window_li.clear()
            self.w_pane_li.clear()
            ws = self.tmux_mgr.set_session(event.item.label)
            for w in ws:
                self.w_window_li.append(MouselessLabelItem(w)) 
        elif event.control.id == "tmuxmodal_window_li":
            self.w_pane_li.clear()
            for p in self.tmux_mgr.set_window(event.item.label):
                self.w_pane_li.append(MouselessLabelItem(p))
        elif event.control.id == "tmuxmodal_pane_li":
            self.tmux_mgr.set_pane(event.item.label)
        self.query_one("#tmuxmodal_session_chosen",Label).update(self.tmux_mgr.session_name)
        self.query_one("#tmuxmodal_window_chosen",Label).update(self.tmux_mgr.window_name)
        self.query_one("#tmuxmodal_pane_chosen",Label).update(self.tmux_mgr.pane_indx)
        return

    def build_sessions(self):
        sessions = self.tmux_mgr.get_sessions() 
        for s in sessions:
            self.w_session_li.append(MouselessLabelItem(s)) 
        if self.tmux_mgr.session_name != "" and self.tmux_mgr.session_name in sessions:
            self.query_one("#tmuxmodal_session_chosen",Label).update(self.tmux_mgr.session_name)
            self.build_windows()
        else:
            self.set_focus(self.w_session_li)

    def build_windows(self):
        windows = self.tmux_mgr.get_windows()
        for w in windows:
            self.w_window_li.append(MouselessLabelItem(w))
        if self.tmux_mgr.window_name != "" and self.tmux_mgr.window_name in windows:
            self.query_one("#tmuxmodal_window_chosen",Label).update(self.tmux_mgr.window_name)
            self.build_panes()
        else:
            self.set_focus(self.w_window_li)


    def build_panes(self):
        panes = self.tmux_mgr.get_panes()
        for p in panes:
            self.w_pane_li.append(MouselessLabelItem(p))
        if str(self.tmux_mgr.pane_indx) != "" and str(self.tmux_mgr.pane_indx) in panes:
            self.query_one("#tmuxmodal_pane_chosen",Label).update(str(self.tmux_mgr.pane_indx))
            self.set_focus(self.w_ok_bt)
        else:
            self.set_focus(self.w_pane_li)
