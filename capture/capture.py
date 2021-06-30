import os
from datetime import datetime
from picamera import PiCamera
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
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
        self.camera = PiCamera()
        self.camera.resolution = (1944, 1944)
        self.camera.start_preview(fullscreen=False, window=(198, 33, 553, 540))

    def home_btn(self):
        self.camera.close()
        App.get_running_app().sm.current = "Home"

    def back_btn(self):
        self.camera.close()
        App.get_running_app().sm.current = self.prev_scr

    def set_page_refs(self, screen):
        """
        Set previous pag accessed from, allowing for back button to return to
        project browser or home screen.
        """
        self.prev_scr = screen

    def capture_btn(self):
        """
        Initialise a sample object and save in the temp directory.

        *****

        1 - create sample object with project as temp
        2 - pass sample object to analysis page
        3 - call sample deletion instead of whatever whay we're doing now if we
        quit analysis page.
        """
        capture_datetime = datetime.today().strftime("%d-%m-%Y-%H-%M-%S")

        # Assing names for captured images
        imgs = {"SD": F"SD-{capture_datetime}.png",
                "IR": F"IR-{capture_datetime}.png"}

        # Init temp project and sample
        temp_p = data_models.Project(json_path=DirConfig.temp_project_json)
        sample = data_models.Sample(name=capture_datetime,
                                    project=temp_p, imgs=imgs)

        # !!!!!!! temp - - - - - - - - -
        if DirConfig.runtype == "dev":
            from PIL import Image
            import random
            colour = (random.randint(0, 255),
                      random.randint(0, 255),
                      random.randint(0, 215))
            image = Image.new('RGB', (1000, 1000), colour)
            image.save(F"{sample.path}{imgs['SD']}", "PNG")
            colour = (colour[0], colour[1], colour[2]+40)
            image = Image.new('RGB', (1000, 1000), colour)
            image.save(F"{sample.path}{imgs['IR']}", "PNG")

        elif DirConfig.runtype == "pi":
            self.camera.capture(F"{sample.path}{imgs['SD']}")
            self.camera.capture(F"{sample.path}{imgs['IR']}")
        # !!!!!!! temp - - - - - - - - -

        # Close camera preview and move to analysis screen
        self.camera.close()
        analysis_scr = App.get_running_app().sm.get_screen("Analysis")
        analysis_scr.set_page_refs(App.get_running_app().sm.current,
                                   sample,
                                   temp_sample=True)
        App.get_running_app().sm.current = "Analysis"


class AnalysisPage(Screen):
    """
    Ref: "Analysis"

    Page showing analystics of image. Can be accessed immediately after image
    taken, or through project page.
    """

    def __init__(self, **kwargs):
        super(AnalysisPage, self).__init__(**kwargs)
        self.add_widget(widgets.NavBar())

    def home_btn(self):
        if self.temp_sample:
            self.popup = AnalysisQuitPopup(self, "Home")
            self.popup.open()
        else:
            App.get_running_app().sm.current = "Home"

    def back_btn(self):
        if self.temp_sample:
            self.popup = AnalysisQuitPopup(self, "Back")
            self.popup.open()
        else:
            App.get_running_app().sm.current = self.prev_screen

    def set_page_refs(self, prev_screen, sample, temp_sample=False):
        """
        Function to set references for images displayed on analysis page.
        *** MUST BE CALLED BEFORE OPENING PAGE ***

        Args:
            prev_screen - str name of the prevously opened screen - allows for
            back button to work for analysis access via both new capture and
            project view page.
            sample - sample object for sample to be analysed
            temp_sample - sets whether images passed are freshly captured,
            therefore warnings must be put inplace to prevent accidental
            deletion (i.e on back button clicked).
        """
        self.prev_screen = prev_screen
        self.sample = sample
        self.ids.sample_img.source = F"{self.sample.path}{self.sample.imgs['SD']}"
        self.temp_sample = temp_sample

    def analyse_btn(self):
        print("ANALYSIS BUTTON CLICKED")

    def save_btn(self, **kwargs):
        """
        Save functionality for moving images to a project.

        kwargs:
            follow_action - action to take following save - pass "Back" or
            "Home" for back/home buttons (i.e complete this action after save)
        """
        self.popup = SaveSampleProjectPopup(self, **kwargs)
        self.popup.open()

    def save_to_project(self, project, s_name):
        """
        Function to save sample to passed project.
        """
        self.sample.save_to_project(project,
                                    name=s_name,
                                    delete=self.temp_sample)
        self.set_page_refs(self.prev_screen, self.sample)  # Reassign page refs

    def delete_imgs(self):
        """
        Called from confirm popup when leaving the Analysis screen on a temp
        sample.
        """
        self.sample.delete_sample()

    def hotswap_pic_btn(self):
        """
        Button to swap image between IR and SD imgs.
        """
        F"{self.sample.path}{self.sample.imgs['SD']}"
        if self.ids.sample_img.source == F"{self.sample.path}{self.sample.imgs['SD']}":
            self.ids.sample_img.source = F"{self.sample.path}{self.sample.imgs['IR']}"
        elif self.ids.sample_img.source == F"{self.sample.path}{self.sample.imgs['IR']}":
            self.ids.sample_img.source = F"{self.sample.path}{self.sample.imgs['SD']}"


class AnalysisQuitPopup(Popup):
    """
    Popup to warn of image discard when leaving analysis page, and offers to
    save. If yes selected, open up the save popup and pass in the button
    functionality (Home/Back) to complete action once save complete.
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
            App.get_running_app().sm.current = self.holder.prev_screen

    def cancel(self):
        pass


class SaveSampleProjectPopup(Popup):
    """
    Popup to select project to save sample to.
    """

    def __init__(self, holder, follow_action=None, **kwargs):
        self.holder = holder
        self.follow_action = follow_action
        super(SaveSampleProjectPopup, self).__init__(**kwargs)
        self.list_projects()

    def list_projects(self):
        """
        Get a list of all projects available to save sample to.
        """
        print("new list_projects")
        self.ids.project_grid.clear_widgets()  # Clear current button list

        # Get all project directories in main project dir and sort
        entries = os.scandir(DirConfig.project_dir)
        dirs = [e for e in entries if os.path.isdir(e)]
        dirs.sort(key=lambda d: d.name.lower())

        for d in dirs:
            project = data_models.Project(json_path=F"{DirConfig.project_dir}{d.name}/{d.name}.json")
            project_line = widgets.ProjectLine(project)
            project_line.bind(on_release=self.p_btn_click_popup)
            self.ids.project_grid.add_widget(project_line)

    def p_btn_click_popup(self, instance):
        """
        Handles initialisation of new popup from project selection.
        """
        p_selection = instance.ids.p_name.text
        p_json = F"{DirConfig.project_dir}{p_selection}/{p_selection}.json"
        project = data_models.Project(json_path=p_json)
        self.popup = SaveSampleNamePopup(self.holder,
                                         project,
                                         self)
        self.popup.title = project.name
        self.popup.open()


        # p_selection = instance.text
        # s_name = self.s_name
        # self.holder.save_to_project(p_selection, s_name)
        # self.dismiss()
        # if self.follow_action == "Home":
        #     App.get_running_app().sm.current = "Home"
        # elif self.follow_action == "Back":
        #     App.get_running_app().sm.current = "New Capture"

class SaveSampleNamePopup(Popup):
    """
    Popup showing project contents and allowing for sample name allocation.
    """

    def __init__(self, holder, project, p_popup, **kwargs):
        """
        Initialise with the project required for popup and the holding page
        (analysis) to allow for sample saving.

        Args:
            holder - Analysis page object allowing for save sample method to be
            called
            project - selected project object from previous popup
            p_popup - previous popup object allowing for dismissal on
            completion
        """
        self.holder = holder
        self.project = project
        self.p_popup = p_popup
        super(SaveSampleNamePopup, self).__init__(**kwargs)
        self.ids.save_s_btn.disabled = True  # save btn disabled without input
        self.list_samples()

    def list_samples(self):
        """
        Search through project sample dict and add a button to popup for
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

    def on_s_name_text(self, s_name):
        """
        Deactivates save button if sample name input field is empty.
        """
        self.ids.save_s_btn.disabled = False
        if s_name == "":
            self.ids.save_s_btn.disabled = True

    def s_btn_click(self, instance):
        """
        Handler funciton for clicking a sample in save window, adds name of the
        selected sample to the save text input.
        """
        self.ids.sample_name_input.text = instance.text

    def save_btn(self):
        """
        Handler for save button clicked. Check if sample name exists and
        confirm overwrite required.
        """
        self.s_name = self.ids.sample_name_input.text

        # Check if sample name already in project and confirm overwrite
        if self.s_name in self.project.samples.keys():
            self.popup = OverwriteSamplePopup(self)
            self.popup.open()
        else:
            self.save_sample()
            self.dismiss()
            self.p_popup.dismiss()

    def save_sample(self):
        """
        Allows for calling from save_btn function and overwrite popup kv file.
        """
        self.holder.save_to_project(self.project, self.s_name)
        if self.p_popup.follow_action == "Home":
            App.get_running_app().sm.current = "Home"
        elif self.p_popup.follow_action == "Back":
            App.get_running_app().sm.current = "New Capture"


class OverwriteSamplePopup(Popup):
    """
    Popup to confirm whether sample with the same name should be overwritten.
    """

    def __init__(self, p_popup, **kwargs):
        """
        Initilaise popup with name of sample to be overwritten.

        Args:
            p_popup - previous popup object, allowing for access to sample
            details and dismissal
        """
        self.p_popup = p_popup
        super(OverwriteSamplePopup, self).__init__(**kwargs)
        s_name = p_popup.s_name
        warn = F"Sample {s_name} will be overwritten. Do you wish to continue?"
        self.title = warn

    def confirm_btn(self):
        """
        Confirms overwrite, closes both popup windows and calls analysis page
        save function.
        """
        self.p_popup.save_sample()
        self.p_popup.dismiss()
        self.p_popup.p_popup.dismiss()
        self.dismiss()
