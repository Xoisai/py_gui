import os
from datetime import datetime
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.app import App
from tex_py_gui import widgets
from tex_py_gui.config import DirConfig

# TEMP - REMOVE ON ACTUAL
from PIL import Image


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

    def capture_btn(self):
        # !!!!!!! temp - - - - - - - - -
        capture_datetime = datetime.today().strftime("%Y-%m-%d-%H-%M-%S")
        img_name = F"temp-{capture_datetime}"
        image = Image.new('RGB', (1000, 1000), (100, 100, 150))
        image.save(F"{DirConfig.temp_dir}{img_name}.png", "PNG")
        # !!!!!!! temp - - - - - - - - -
        analysis_scr = App.get_running_app().sm.get_screen("Analysis")
        analysis_scr.set_image_name(img_name)
        App.get_running_app().sm.current = "Analysis"


class AnalysisPage(Screen):
    """
    Ref: "Analysis"

    Page with newly captured image.
    """

    def __init__(self, **kwargs):
        super(AnalysisPage, self).__init__(**kwargs)
        self.add_widget(widgets.NavBar())

    def home_btn(self):
        self.popup = AnalysisQuitPopup(self, "Home")
        self.popup.open()

    def back_btn(self):
        self.popup = AnalysisQuitPopup(self, "Back")
        self.popup.open()

    def recapture_btn(self):
        self.popup = AnalysisQuitPopup(self, "Recapture")
        self.popup.open()

    def set_image_name(self, img_name):
        """
        Function to set the temp name of images captured on capture screen, in
        order to display correct image.
        """
        self.img_name = img_name
        self.img_path = F"{DirConfig.temp_dir}{self.img_name}.png"
        self.ids.sample_img.source = self.img_path

    def analyse_btn(self):
        print("ANALYSIS BUTTON CLICKED")

    def save_btn(self):
        self.popup = SaveSamplePopup(self)
        self.popup.open()

    def delete_imgs(self):
        os.remove(self.img_path)


class AnalysisQuitPopup(Popup):
    """
    Popup to warn of image discard when leaving analysis page.
    """

    def __init__(self, holder, btn_function, **kwargs):
        self.holder = holder
        self.btn_function = btn_function
        super(AnalysisQuitPopup, self).__init__(**kwargs)

    def enter(self):
        """
        Confirmation of discarding current sample image, checks if button click
        is home or back/recapture.
        """
        self.holder.delete_imgs()
        if self.btn_function == "Home":
            App.get_running_app().sm.current = "Home"
        else:
            App.get_running_app().sm.current = "New Capture"

    def cancel(self):
        pass


class SaveSamplePopup(Popup):
    """
    Popup to select project to save sample to, and name sample.
    """

    def __init__(self, holder, **kwargs):
        self.holder = holder
        super(SaveSamplePopup, self).__init__(**kwargs)

    # def enter(self):
    #     """
    #     Confirmation of discarding current sample image, checks if button click
    #     is home or back/recapture.
    #     """
    #     self.holder.delete_imgs()
    #     if self.btn_function == "Home":
    #         App.get_running_app().sm.current = "Home"
    #     else:
    #         App.get_running_app().sm.current = "New Capture"
