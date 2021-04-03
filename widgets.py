from datetime import datetime
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.behaviors import ButtonBehavior


class NavBar(FloatLayout):
    """
    Navigation wdiget with 'home' and 'back' buttons.
    """
    pass


class ThumbnailButton(Button):
    """
    Button with thumbnail image to be added python side.
    """
    pass


class ButtonHtlImg(ButtonBehavior, GridLayout):
    """
    Button with text and image, aligned horizontally.
    """
    pass


class ProjectLine(ButtonBehavior, GridLayout):
    """
    Line to be shown in project browser detailing project name and creation
    date.
    """
    def __init__(self, project, **kwargs):
        super(ProjectLine, self).__init__(**kwargs)
        self.ids.p_name.text = project.name
        c_date = datetime.strptime(project.creation_datetime,
                                   "%Y-%m-%d-%H:%M:%S")
        self.ids.c_date.text = c_date.strftime("%Y-%m-%d")
        self.ids.n_samples.text = str(len(project.samples))


class ProjectLineHeader(GridLayout):
    """
    Column titles for project browser
    """
    pass
