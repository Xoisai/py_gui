import os
import cv2
import matplotlib.pyplot as plt
from skimage import img_as_ubyte
from datetime import datetime
from picamera import PiCamera
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.app import App
from tex_py_gui import widgets
from tex_py_gui.config import DirConfig, ModelConfig
from tex_py_gui.data import data_models

# Temp!
from tex_py_img_processing.image_inferencer import ImageInferencer
from tex_py_img_processing.image_processor import ImageProcessor
from tex_py_img_processing.postprocessor import Postprocessor
from tex_py_img_processing.config import DefaultConfig


class NewCapPage(Screen):
    """
    Ref: "New Capture"

    Page to handle capture of new sample image.
    """

    def __init__(self, **kwargs):
        super(NewCapPage, self).__init__(**kwargs)
        self.add_widget(widgets.NavBar())

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
        self.camera = PiCamera()
        self.camera.resolution = (600, 600)
        self.camera.start_preview(fullscreen=False, window=(180, 30, 585, 540))

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

        # Assign name for captured image
        imgs = {"SD": F"SD-{capture_datetime}.png"}

        # Init temp project and sample
        temp_p = data_models.Project(json_path=DirConfig.temp_project_json)
        sample = data_models.Sample(name=capture_datetime,
                                    project=temp_p, imgs=imgs)

        # !!!!!!! temp - - - - - - - - -
        
#         NEED TO WORK OUT WHERE THIS IS GOING TO SIT IN THE WHOLE PROCESS FLOW
        def resize_img(img, scale, dims=None):
            """
            Resize an image based on supplied scale factor. If dims arg is
            passed, will instead resize to dims (width, height).
            """
            if dims is None:
                dims = (int(img.shape[1] * scale), int(img.shape[0] * scale))
            resized = cv2.resize(img, dims, interpolation=cv2.INTER_AREA)
            return resized
        
        if DirConfig.runtype == "dev":
            from PIL import Image
            import random
            colour = (random.randint(0, 255),
                      random.randint(0, 255),
                      random.randint(0, 215))
            image = Image.new('RGB', (1000, 1000), colour)
            image.save(F"{sample.path}{imgs['SD']}", "PNG")

#         This is a long and convoluted way of getting a square image. Currently
#         we can't cature directly into an np array at full resolution, so the
#         next best method is just to capture, save, read in, modify, delete
#         original and resave at same path.
        elif DirConfig.runtype == "pi":
            self.camera.resolution = (2050, 1944)
            self.camera.capture(F"{sample.path}{imgs['SD']}")
            self.camera.resolution = (600, 600)
            img = cv2.imread(F"{sample.path}{imgs['SD']}")
            img = img[:, 106:]
            img = resize_img(img, 0.43)
            os.remove(F"{sample.path}{imgs['SD']}")
            cv2.imwrite(F"{sample.path}{imgs['SD']}", img)
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
        self.model_path = ModelConfig.model_paths["hydrophobic"]

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
        self.ids.droplet_hist.source = "static/hist_template.png"
        self.temp_sample = temp_sample

        # Check if sample has been analysed to add image switch button
        if self.sample.analysed:
            self.ids.hotswap_btn.disabled = False
            self.ids.analysis_btn.disabled = True
            self.ids.droplet_hist.source = F"{self.sample.path}{self.sample.imgs['HS']}"

        else:
            self.ids.hotswap_btn.disabled = True
            self.ids.analysis_btn.disabled = False
            
    def activate_loading_gif(self):
        self.ids.loading_icon.opacity = 1.0
        self.ids.analysis_btn_icon.opacity = 0.0
        
    def deactivate_loading_gif(self):
        self.ids.loading_icon.opacity = 0.0
        self.ids.analysis_btn_icon.opacity = 1.0

    def analyse_btn(self):
        """

        """
        # Analyse image
        # TEMP!!!
        img_path =  F"{self.sample.path}{self.sample.imgs['SD']}"
        out_dir = self.sample.path
        out_name = F"AN-{datetime.today().strftime('%d-%m-%Y-%H-%M-%S')}.png"
        self.sample.imgs["AN"] = out_name
        hist_name = F"HS-{datetime.today().strftime('%d-%m-%Y-%H-%M-%S')}.png"
        self.sample.imgs["HS"] = hist_name
        
        # Create inference and processing instances
        inferencer = ImageInferencer(self.model_path, int_quantised=True,
                                     num_threads=4)
        processor = ImageProcessor(inferencer)
        
        # Read in image, run through network
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        analysed = processor.analyse_image(img)
        
        # TEMP FAFFY HACKY WAY TO FIX BUG Postprocess network output (********************)
        src_img = cv2.imread(img_path)  # Update this, simply convert to greyscale above when calling analysis
#         cv2.imwrite(os.path.join(out_dir, out_name), img_as_ubyte(analysed))
#         analysed = cv2.imread(os.path.join(out_dir, out_name), cv2.IMREAD_GRAYSCALE)
        postprocessor = Postprocessor(src_img, img_as_ubyte(analysed))
#         os.remove(os.path.join(out_dir, out_name))
        
        # Save droplet map
        droplet_map = postprocessor.get_contmap()
        cv2.imwrite(os.path.join(out_dir, out_name), droplet_map)
        
        # Save droplet histogram and add to analysis page
        hist = postprocessor.get_droplet_histogram()
        hist.savefig(os.path.join(out_dir, hist_name))
        self.ids.droplet_hist.source = os.path.join(out_dir, hist_name)
        
        # Display statistics
        stats_dict = postprocessor.get_droplet_statistics()
        self.assign_stats(stats_dict)

        # Check if analysis image available and activate hotswap button
        if "AN" in self.sample.imgs.keys():
            self.ids.hotswap_btn.disabled = False
            self.ids.analysis_btn.disabled = True
            self.sample.analysed = True
            
    def assign_stats(self, stats_dict):
        """
        Takes statistics dictionary and assigns output to statistics pane.
        """
        self.ids.sample_area_cm2.text = str(stats_dict["areas"]["sample_area_cm2"])
        self.ids.droplet_area_cm2.text = str(stats_dict["areas"]["droplet_area_cm2"])
        self.ids.sample_coverage.text = str(stats_dict["areas"]["droplet_coverage_perc"])
        self.ids.avg_droplet_size.text = str(stats_dict["areas"]["droplet_area_mean_cm2"])
        self.ids.droplet_number.text = str(stats_dict["num_droplets"])
        
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
        
    def settings_btn(self, **kwargs):
        """
        Triggers popup with analysis settings.
        """
        self.popup = AnalysisSettingsPopup(self, **kwargs)
        self.popup.open()

    def hotswap_pic_btn(self):
        """
        Button to swap image between IR and SD imgs.
        """
        F"{self.sample.path}{self.sample.imgs['SD']}"
        if self.ids.sample_img.source == F"{self.sample.path}{self.sample.imgs['SD']}":
            self.ids.sample_img.source = F"{self.sample.path}{self.sample.imgs['AN']}"
        elif self.ids.sample_img.source == F"{self.sample.path}{self.sample.imgs['AN']}":
            self.ids.sample_img.source = F"{self.sample.path}{self.sample.imgs['SD']}"
            
    def update_model(self, model_type):
        """
        Function to take a model type string and update the currently used
        model.
        """
        self.model_path = ModelConfig.model_paths[model_type]


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
        
class AnalysisSettingsPopup(Popup):
    """
    Popup to select project to save sample to.
    """

    def __init__(self, holder, **kwargs):
        self.holder = holder
        super(AnalysisSettingsPopup, self).__init__(**kwargs)

    def toggle_model_type(self, model_type):
        """
        Function to call analysis page model path update function for
        subsequent analysis.
        """
        self.holder.update_model(model_type)
