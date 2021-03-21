import os
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from tex_py_gui.config import DirConfig
from tex_py_gui import widgets


class ProjectBrowserPage(Screen):
    """
    Ref: "Project Browser"

    Project browser screen listing all current projects.
    """

    def __init__(self, **kwargs):
        super(ProjectBrowserPage, self).__init__(**kwargs)
        self.add_widget(widgets.NavBar())
        self.list_projects()

    def home_btn(self):
        App.get_running_app().sm.current = "Home"

    def back_btn(self):
        App.get_running_app().sm.current = "Home"

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
        p_selection = instance.text
        view_scr = App.get_running_app().sm.get_screen("Project View")
        view_scr.set_project(p_selection)
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
        self.add_project_dir(self.project_name)
        self.holder.list_projects()
        self.dismiss()

    def add_project_dir(self, p_name):
        """
        Add a project directory to main data dir.
        """
        dir_path = F"{DirConfig.project_dir}{p_name}"
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)


class ProjectViewPage(Screen):

    def __init__(self, **kwargs):
        super(ProjectViewPage, self).__init__(**kwargs)
        self.add_widget(widgets.NavBar())

    def home_btn(self):
        App.get_running_app().sm.current = "Home"

    def back_btn(self):
        App.get_running_app().sm.current = "Project Browser"

    def set_project(self, p_name):
        """
        Function called before transitioning to the project view page. Assigns
        relevant values to the screen, specific to the selected project.
        """
        self.p_name = p_name
        self.ids.p_name_lbl.text = self.p_name
        self.project_dir = F"{DirConfig.project_dir}{p_name}"
