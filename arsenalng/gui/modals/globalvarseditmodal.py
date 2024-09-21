from textual.widgets import Input, Label
from textual.containers import Horizontal, VerticalScroll
from textual import events, on

from arsenalng.gui.modals.mouselessmodal import MouselessModal


class GlobalVarsEditModal(MouselessModal):
    focus_save = None
    global_vars = None

    def __init__(self, global_vars, name=None, id=None, classes=None):
        self.inputs = {}
        self.global_vars = global_vars
        super().__init__(name=name, id=id, classes=classes)

    def compose(self):
        with VerticalScroll():
            for name, value in self.global_vars.items():
                self.inputs[name] = Input(id=name, placeholder="", type="text", value=value)
                yield self.inputs[name]
                self.inputs[name].border_title = name

    def on_mount(self) -> None:
        if len(self.inputs):
            self.set_focus(self.inputs[next(iter(self.inputs.keys()))])
            self.focus_save = self.focused

    @on(Input.Changed)
    def recompute_table(self, event: Input.Changed):
        self.global_vars[event.input.id] = event.input.value 

    def on_key(self, event: events.Key) -> None:
        event.stop()
        if event.key in ["tab", "down", "shift+tab", "up"]:
            if event.key == "tab" or  event.key == "down":
                self.focus_next()
                #if self.focused == self.infobox:
                #    self.focus_next()
            elif event.key == "shift+tab" or event.key == "up":
                self.focus_previous()
                #if self.focused == self.infobox:
                #    self.focus_previous()
            self.focus_save = self.focused
            self.query_one(VerticalScroll).scroll_to_widget(self.focused)
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
        elif event.key == "escape" or event.key == "enter":
            self.dismiss(self.global_vars)
