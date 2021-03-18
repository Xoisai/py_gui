import os
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty
from tex_py_gui.config import DirConfig


class NewProjectPopup(Popup):
    """
    Popup for new project creation.
    """

    project_name = ObjectProperty()  # Input project name

    def __init__(self, **kwargs):
        super(NewProjectPopup, self).__init__(**kwargs)

    def enter(self):
        print(F"Project name input is {self.project_name}")
        add_project_dir(self.project_name)
        self.dismiss()


def add_project_dir(p_name):
    """
    Add a project directory to main data dir.
    """
    dir_path = F"{DirConfig.project_dir}{p_name}"
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
