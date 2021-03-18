from tex_py_gui.config import DirConfig  # noqa: F401
import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from tex_py_gui.browser import browser
kivy.require("2.0.0")


class HomePage(Screen):

    def new_cap_btn(self):
        app.sm.current = "New Capture"

    def p_browse_btn(self):
        app.sm.current = "Project Browser"

    def settings_btn(self):
        app.sm.current = "Settings"


class NewCapPage(Screen):

    def home_btn(self):
        app.sm.current = "Home"

    def back_btn(self):
        print("NEW CAP BACK CLICKED")


class ProjectBrowserPage(Screen):

    def home_btn(self):
        app.sm.current = "Home"

    def back_btn(self):
        print("PROJECT BROWSE BACK CLICKED")

    def add_project(self):
        self.popup = browser.NewProjectPopup()
        self.popup.open()


class SettingsPage(Screen):
    pass


class TextileGui(App):

    def build(self):

        # Create screen namager object
        self.sm = ScreenManager()

        # Add screens to project
        self.sm.add_widget(HomePage(name="Home"))
        self.sm.add_widget(NewCapPage(name="New Capture"))
        self.sm.add_widget(ProjectBrowserPage(name="Project Browser"))
        self.sm.add_widget(SettingsPage(name="Settings"))

        return self.sm


if __name__ == "__main__":
    app = TextileGui()
    app.run()
