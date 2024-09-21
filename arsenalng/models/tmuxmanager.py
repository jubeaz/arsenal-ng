import libtmux
import random
import string
import time


class TmuxManager:
    server = None
    session = None
    session_name = ""
    window = None
    window_name = ""
    is_new_window = False
    pane = None
    pane_indx = ""


    def __init__(self, server):
        self.server = server
        assert self.server.is_alive()
        self.session = None
        self.session_name = ""
        self.window = None
        self.window_name = ""
        self.is_new_window = False
        self.pane = None
        self.pane_indx = ""

    def get_sessions(self):
        return [s.name for s in self.server.sessions]
    
    def get_windows(self):
        windows = []
        windows = [f"{w.index}:{w.name}" for w in self.session.windows]
        windows.append("<new_window>")
        return windows

    def set_session(self, name):
        try:
            self.session = self.server.sessions.get(session_name=name)
        except libtmux._internal.query_list.ObjectDoesNotExist:
            raise RuntimeError(f"Could not find session {self.arsenalng_global_vars["arsenalng_session_name"]}") from None 
        self.session_name  = name
        self.window_name = ""
        self.window = None
        self.pane_indx = ""
        self.pane = None
        return self.get_windows()

    def get_panes(self):
        panes = []
        if self.is_new_window is False:
            panes = [p.index for p in self.window.panes]
            panes.append("<all_panes>")
        panes.append("<new_pane>")
        return panes

    def set_window(self, name):
        self.window_name = name
        self.pane_indx = ""
        self.pane = None
        self.is_new_window = False
        if name != "<new_window>":
            try:
                indx = int(name.split(":", 1)[0])
                search_name = name.split(":", 1)[1]
                self.window = self.session.select_window(search_name)
            except libtmux.exc.LibTmuxException:
                self.is_new_window = True
        else:
            self.is_new_window = True
        return self.get_panes()

    def set_pane(self, indx):
        if self.is_new_window:
            self.pane_indx = "0"
        else:
            self.pane_indx = indx
    
    def finalize(self):
        if self.window_name == "<new_window>":
            self.window_name = "".join(random.choices(string.ascii_letters + string.digits, k=16))
        if self.is_new_window:
            self.window = self.session.new_window(attach=False, window_name=self.window_name)
            self.pane = self.window.panes[0]
            self.pane_indx = 0
        elif self.pane_indx == "<new_pane>":
            self.pane_indx = len(self.window.panes) + 1
            self.pane = self.window.split_window(attach=False)
            time.sleep(0.3)
        elif self.pane_indx == "<all_panes>": 
            self.pane_indx = None
            self.pane = None
        else:
            self.pane_indx = int(self.pane_indx)
            self.pane = self.window.panes[self.pane_indx]    
    
    def is_finalizable(self):
        return self.session_name != "" and self.window_name != "" and self.pane_indx != "" 