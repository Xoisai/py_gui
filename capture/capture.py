from kivy.uix.screenmanager import Screen
from kivy.app import App
from tex_py_gui import widgets


class NewCapPage(Screen):
    """
    Ref: "New Capture"

    Page to handle capture of new sample image.
    """

    def __init__(self, **kwargs):
        super(NewCapPage, self).__init__(**kwargs)
        self.add_widget(widgets.NavBar())

    def home_btn(self):
        App.get_running_app().sm.current = "Home"

    def back_btn(self):
        App.get_running_app().sm.current = "Home"
