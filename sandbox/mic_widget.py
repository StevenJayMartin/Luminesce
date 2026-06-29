
from textual.widget import Widget
from textual.reactive import reactive

class MicWidget(Widget):
    blinking = reactive(False)
    visible_state = reactive(False)

    def on_mount(self):
        self.set_interval(0.5, self._toggle)

    def _toggle(self):
        if self.blinking:
            self.visible_state = not self.visible_state
        else:
            self.visible_state = False

    def render(self):
        if not self.visible_state:
            return ""
        return "🎤 Listening..."

