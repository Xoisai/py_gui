import os
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from tex_py_gui.config import DirConfig
from kivy.app import App


class ProjectBrowserPage(Screen):

    def __init__(self, **kwargs):
        super(ProjectBrowserPage, self).__init__(**kwargs)
        self.p_btn_scroll = None
        self.list_projects()

    def home_btn(self):
        App.get_running_app().sm.current = "Home"

    def back_btn(self):
        print("PROJECT BROWSE BACK CLICKED")

    def add_project(self):
        self.popup = NewProjectPopup(self)
        self.popup.open()

    def list_projects(self):
        self.ids.p_btn_grid.clear_widgets()  # Clear current button list

        # Get all project directories in main project dir and sort
        entries = os.scandir(DirConfig.project_dir)
        dirs = [e for e in entries if os.path.isdir(e)]
        dirs.sort(key=lambda d: d.name.lower())

        # Add button for each project
        for d in dirs:
            btn = Button(text=d.name)
            btn.bind(on_release=self.p_btn_click)
            self.ids.p_btn_grid.add_widget(btn)

    def p_btn_click(self, instance):
        App.get_running_app().sm.current = "Project View"


class NewProjectPopup(Popup):
    """
    Popup for new project creation.
    """

    project_name = ObjectProperty()  # Input project name

    def __init__(self, holder, **kwargs):
        self.holder = holder
        super(NewProjectPopup, self).__init__(**kwargs)

    def enter(self):
        add_project_dir(self.project_name)
        self.holder.list_projects()
        self.dismiss()


def add_project_dir(p_name):
    """
    Add a project directory to main data dir.
    """
    dir_path = F"{DirConfig.project_dir}{p_name}"
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


class ProjectViewPage(Screen):

    def __init__(self, **kwargs):
        super(ProjectViewPage, self).__init__(**kwargs)

    def home_btn(self):
        App.get_running_app().sm.current = "Home"
