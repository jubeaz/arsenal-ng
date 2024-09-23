from textual.widgets import Label, ListView
from textual.containers import Horizontal, Vertical
from textual import events

from arsenalng.models.tmuxmanager import TmuxManager
from arsenalng.gui.modals.mouselessmodal import MouselessModal
from arsenalng.gui.widgets.mouselesslistview import MouselessListView
from arsenalng.gui.widgets.mouselesslabelitem import MouselessLabelItem

class TmuxModal(MouselessModal):
    arsenalng_global_vars = None
    tmux_mgr = None

    w_session = None
    w_window = None
    w_pane = None
    focus_save = None

    def __init__(self, arsenalng_global_vars, tmux_mgr: TmuxManager, name=None, id=None, classes=None):  # noqa: A002
        self.arsenalng_global_vars = arsenalng_global_vars
        self.tmux_mgr = tmux_mgr
        super().__init__(name=name, id=id, classes=classes)

    def compose(self):
        with Vertical( ):
            with Horizontal(id="tmuxmodal_horizontal_top"):
                yield Label("",id="tmuxmodal_session_chosen")
                yield Label("",id="tmuxmodal_window_chosen")
                yield Label("",id="tmuxmodal_pane_chosen")
            with Horizontal(id="tmuxmodal_horizontal_bottom"):
                yield MouselessListView(id="tmuxmodal_session")
                yield MouselessListView(id="tmuxmodal_window")
                yield MouselessListView(id="tmuxmodal_pane")

    def on_mount(self) -> None:
        self.w_session = self.query_one("#tmuxmodal_session")
        self.w_session.border_title = "Session"
        self.w_window = self.query_one("#tmuxmodal_window")
        self.w_window.border_title = "Window"
        self.w_pane = self.query_one("#tmuxmodal_pane")
        self.w_pane.border_title = "Pane (pfx-q)"
        self.build_sessions()
        self.focus_save = self.focused

    def on_key(self, event: events.Key) -> None:
        event.stop()
        if event.key == "escape":
            self.dismiss()
        elif event.key == "enter" and self.tmux_mgr.is_finalizable():
                self.tmux_mgr.finalize()
                self.dismiss(self.tmux_mgr)
        elif event.key == "space":
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
        if event.control.id == "tmuxmodal_session":
            self.w_window.clear()
            self.w_pane.clear()
            ws = self.tmux_mgr.set_session(event.item.label)
            for w in ws:
                self.w_window.append(MouselessLabelItem(w)) 
        elif event.control.id == "tmuxmodal_window":
            self.w_pane.clear()
            for p in self.tmux_mgr.set_window(event.item.label):
                self.w_pane.append(MouselessLabelItem(p))
        elif event.control.id == "tmuxmodal_pane":
            self.tmux_mgr.set_pane(event.item.label)
        self.query_one("#tmuxmodal_session_chosen",Label).update(self.tmux_mgr.session_name)
        self.query_one("#tmuxmodal_window_chosen",Label).update(self.tmux_mgr.window_name)
        self.query_one("#tmuxmodal_pane_chosen",Label).update(self.tmux_mgr.pane_indx)
        return

    def build_sessions(self):
        sessions = self.tmux_mgr.get_sessions() 
        for s in sessions:
            self.w_session.append(MouselessLabelItem(s)) 
        if self.tmux_mgr.session_name != "" and self.tmux_mgr.session_name in sessions:
            self.query_one("#tmuxmodal_session_chosen",Label).update(self.tmux_mgr.session_name)
            self.build_windows()
        else:
            self.set_focus(self.w_session)
            self.tmux_mgr.empty_selection()

    def build_windows(self):
        windows = self.tmux_mgr.get_windows()
        for w in windows:
            self.w_window.append(MouselessLabelItem(w))
        if self.tmux_mgr.window_name != "" and self.tmux_mgr.window_name in windows:
            self.query_one("#tmuxmodal_window_chosen",Label).update(self.tmux_mgr.window_name)
            self.build_panes()
        else:
            self.set_focus(self.w_window)
            self.tmux_mgr.unset_window()

    def build_panes(self):
        panes = self.tmux_mgr.get_panes()
        for p in panes:
            self.w_pane.append(MouselessLabelItem(p))
        if str(self.tmux_mgr.pane_indx) != "" and str(self.tmux_mgr.pane_indx) in panes:
            self.query_one("#tmuxmodal_pane_chosen",Label).update(str(self.tmux_mgr.pane_indx))
            self.set_focus(self.w_session)
        else:
            self.set_focus(self.w_pane)
            self.tmux_mgr.unset_pane()
