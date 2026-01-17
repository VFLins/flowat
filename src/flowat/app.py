import toga

from flowat import pages


class Flowat(toga.App):
    def startup(self):
        """Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        self.main_page = pages.main.MainSection(app=self)
        main_box = self.main_page.full_contents

        self.group_main = toga.Group(self.formal_name, order=10)
        self.group_help = toga.Group("Ajuda", order=20)

        self.main_window = toga.Window(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()


def main():
    return Flowat()
