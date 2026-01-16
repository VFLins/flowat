from toga import App
from toga.widgets.box import Box


class BaseSection:
    def __init__(self, app: App):
        self._app = app
        self.full_contents = Box()

    def _refresh_layout(self):
        """Set the most appropriate layout to `self.full_contents` for the current
        context. Should be overwritten by it's children.
        """
        self.full_contents.refresh()
