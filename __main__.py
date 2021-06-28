from tex_py_gui.config import DirConfig  # noqa: F401
import os
import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from tex_py_gui.browser import browser
from tex_py_gui.capture import capture
from tex_py_gui.settings import settings
from kivy.lang import Builder
kivy.require("2.0.0")

# Load in kivy design files
for filename in os.listdir(DirConfig.kv_dir):
    if filename.endswith(".kv"):
        Builder.load_file(F"{DirConfig.kv_dir}{filename}")


class HomePage(Screen):

    def new_cap_btn(self):
        new_cap_scr = App.get_running_app().sm.get_screen("New Capture")
        new_cap_scr.set_page_refs(App.get_running_app().sm.current)
        app.sm.current = "New Capture"

    def p_browse_btn(self):
        app.sm.current = "Project Browser"

    def settings_btn(self):
        app.sm.current = "Settings"


class TextileGui(App):

    def build(self):

        # Create screen namager object
        self.sm = ScreenManager()

        # Add screens to project
        self.sm.add_widget(HomePage(name="Home"))
        self.sm.add_widget(capture.NewCapPage(name="New Capture"))
        self.sm.add_widget(capture.AnalysisPage(name="Analysis"))
        self.sm.add_widget(browser.ProjectBrowserPage(name="Project Browser"))
        self.sm.add_widget(browser.ProjectViewPage(name="Project View"))
        self.sm.add_widget(settings.SettingsPage(name="Settings"))

        return self.sm


if __name__ == "__main__":
    app = TextileGui()
    app.run()

    # parser = argparse.ArgumentParser
    # parser.add_argument("--run_mode", "-rm", type=str, default="dev")
