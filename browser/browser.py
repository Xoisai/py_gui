import os
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from tex_py_gui.config import DirConfig
from tex_py_gui import widgets
from tex_py_gui.data import data_models
from tex_py_gui import utils


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
        self.ids.project_grid.clear_widgets()  # Clear current button list
        # self.ids.project_grid.add_widget(widgets.ProjectLineHeader())

        # Get all project directories in main project dir and sort
        entries = os.scandir(DirConfig.project_dir)
        dirs = [e for e in entries if os.path.isdir(e)]
        dirs.sort(key=lambda d: d.name.lower())

        for d in dirs:
            project = data_models.Project(json_path=F"{DirConfig.project_dir}{d.name}/{d.name}.json")
            project_line = widgets.ProjectLine(project)
            project_line.bind(on_release=self.p_btn_click)
            self.ids.project_grid.add_widget(project_line)

    def p_btn_click(self, instance):
        p_selection = instance.ids.p_name.text
        p_view_scr = App.get_running_app().sm.get_screen("Project View")
        p_view_scr.set_project(p_selection)
        App.get_running_app().sm.transition.direction = "left"
        App.get_running_app().sm.current = "Project View"


class NewProjectPopup(Popup):
    """
    Popup for new project creation.
    """

    project_name = ObjectProperty()  # Input project name

    def __init__(self, holder, **kwargs):
        self.holder = holder
        super(NewProjectPopup, self).__init__(**kwargs)
        self.ids.add_p_btn.disabled = True

    def validate_p_name(self, p_name):
        """
        Validation function to ensure project name doesn't already exist.
        """
        self.ids.add_p_btn.disabled = False
        if p_name in utils.get_p_names() or p_name == "":
            self.ids.add_p_btn.disabled = True

    def enter(self):
        self.add_project(self.project_name)
        self.holder.list_projects()
        self.dismiss()

    def add_project(self, p_name):
        """
        Add a project directory to main data dir.
        """
        project = data_models.Project(name=p_name)


class ProjectViewPage(Screen):
    """
    Ref: "Project View"
    """

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
        json_path = F"{DirConfig.project_dir}{p_name}/{p_name}.json"
        self.project = data_models.Project(json_path=json_path)
        self.list_samples()
        self.ids.page_title.text = F"Project {self.project.name}"

    def list_samples(self):
        """
        Search through project sample dict and add a button to project page for
        each.
        """
        self.ids.s_btn_grid.clear_widgets()  # Clear current samples grid

        # Get all samples in project alphabetically and add a button
        for s_name in sorted(self.project.samples, key=lambda s: s.lower()):
            # init sample class
            sample = data_models.Sample(json_path=self.project.samples[s_name])
            btn = widgets.ThumbnailButton()
            btn.text = sample.name
            btn.ids.thumb_img.source = sample.get_image_path("SD")
            btn.bind(on_release=self.s_btn_click)
            self.ids.s_btn_grid.add_widget(btn)

    def s_btn_click(self, instance):
        """
        Open analysis view page (capture application branch) from sample button
        click.
        """
        s_selection = instance.text
        s_json_path = F"{self.project.path}{s_selection}/{s_selection}.json"
        sample = data_models.Sample(json_path=s_json_path)
        s_view_scr = App.get_running_app().sm.get_screen("Analysis")

        # Prepare analysis page for current sample
        s_view_scr.set_page_refs(App.get_running_app().sm.current,
                                 sample)
        App.get_running_app().sm.transition.direction = "left"
        App.get_running_app().sm.current = "Analysis"

    def new_capture_btn(self):
        """
        New capture button to move to new capture page.
        """

        # Prepare new capture page for current project
        new_cap_scr = App.get_running_app().sm.get_screen("New Capture")
        new_cap_scr.set_page_refs(App.get_running_app().sm.current)
        App.get_running_app().sm.transition.direction = "left"
        App.get_running_app().sm.current = "New Capture"
