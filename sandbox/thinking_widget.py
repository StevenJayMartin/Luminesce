
from textual.widget import Widget
from textual.reactive import reactive

class ThinkingWidget(Widget):
    thinking = reactive(False)
    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    index = 0

    def on_mount(self):
        self.set_interval(0.1, self._spin)

    def _spin(self):
        if self.thinking:
            self.index = (self.index + 1) % len(self.frames)
            self.refresh()
        else:
            self.index = 0
            self.refresh()

    def render(self):
        if not self.thinking:
            return ""
        return f"Thinking {self.frames[self.index]}"

