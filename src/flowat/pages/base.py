from toga import App


class BaseSection:
    def __init__(self, app: App):
        self._app = app
