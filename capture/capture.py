import os
from datetime import datetime
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.app import App
from tex_py_gui import widgets
from tex_py_gui.config import DirConfig
from tex_py_gui.data import data_models


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
        # TEMP - REMOVE ON ACTUAL
        from PIL import Image
        capture_datetime = datetime.today().strftime("%Y-%m-%d-%H-%M-%S")
        imgs = {"SD": F"SD-{capture_datetime}.png",
                "IR": F"IR-{capture_datetime}.png"}
        import random
        colour = (random.randint(0, 255),
                  random.randint(0, 255),
                  random.randint(0, 215))
        image = Image.new('RGB', (1000, 1000), colour)
        image.save(F"{DirConfig.temp_dir}{imgs['SD']}", "PNG")
        colour = (colour[0], colour[1], colour[2]+40)
        image = Image.new('RGB', (1000, 1000), colour)
        image.save(F"{DirConfig.temp_dir}{imgs['IR']}", "PNG")
        # !!!!!!! temp - - - - - - - - -
        analysis_scr = App.get_running_app().sm.get_screen("Analysis")
        analysis_scr.set_image_refs(imgs,
                                    DirConfig.temp_dir,
                                    temp_img=True)
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
        if self.temp_img:
            self.popup = AnalysisQuitPopup(self, "Home")
            self.popup.open()
        else:
            App.get_running_app().sm.current = "Home"

    def back_btn(self):
        if self.temp_img:
            self.popup = AnalysisQuitPopup(self, "Back")
            self.popup.open()
        else:
            App.get_running_app().sm.current = "New Capture"

    def recapture_btn(self):
        self.popup = AnalysisQuitPopup(self, "Recapture")
        self.popup.open()

    def set_image_refs(self, imgs, img_dir, temp_img=False):
        """
        Function to set references for images displayed on analysis page.
        *** MUST BE CALLED BEFORE OPENING PAGE ***

        Args:
            imgs - dictionary containing image names for SD and IR images
            img_dir - directory of the images
            temp_img - sets whether images passed are freshly captured,
            therefore warnings must be put inplace to prevent accidental
            deletion (i.e on back button clicked).
        """
        self.imgs = imgs
        self.img_path = F"{img_dir}{self.imgs['SD']}"
        self.ids.sample_img.source = self.img_path
        self.temp_img = temp_img

    def analyse_btn(self):
        print("ANALYSIS BUTTON CLICKED")

    def save_btn(self):
        self.popup = SaveSamplePopup(self)
        self.popup.open()

    def save_to_project(self, p_name, s_name):
        """
        Function to take assigned project, instantiate project class and call
        sample creation method within that project.
        """
        json_path = F"{DirConfig.project_dir}{p_name}/{p_name}.json"
        project = data_models.Project(json_path=json_path)
        sample = data_models.Sample(name=s_name,
                                    project=project,
                                    imgs=self.imgs)

        # Reassign page image refs
        self.set_image_refs(sample.imgs, sample.path)

    def delete_imgs(self):
        for type, img in self.imgs.items():
            os.remove(F"{DirConfig.temp_dir}{img}")


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
        self.list_projects()

    def list_projects(self):
        """
        Get a list of all projects available to save to
        """
        # Get all project directories in main project dir and sort
        entries = os.scandir(DirConfig.project_dir)
        dirs = [e for e in entries if os.path.isdir(e)]
        dirs.sort(key=lambda d: d.name.lower())

        # Add button for each project
        for d in dirs:
            btn = Button(text=d.name)
            btn.bind(on_release=self.p_btn_click_popup)
            self.ids.p_btn_grid_popup.add_widget(btn)

    def p_btn_click_popup(self, instance):
        p_selection = instance.text
        s_name = self.s_name
        self.holder.save_to_project(p_selection, s_name)
        self.dismiss()
