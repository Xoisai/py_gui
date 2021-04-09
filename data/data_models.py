"""
Data models for all objects (projects, samples etc).
"""

import os
import json
import shutil
from datetime import datetime
from tex_py_gui.config import DirConfig


class Project():
    """
    Project object.
    """

    def __init__(self, name=None, json_path=None):
        """
        Either initialises a new project class and saves project data to json,
        or inits directly from project json file, specified by json_path.

        Args:
            name - project name str
            json_path - absolute path to json file containing project data to
            init from.
        """
        if json_path is not None:
            self.read_json(json_path)
        else:
            self.name = name
            self.path = F"{DirConfig.project_dir}{name}/"
            self.json_path = F"{self.path}{self.name}.json"
            self.creation_datetime = datetime.today().strftime("%d-%m-%Y-%H:%M:%S")
            self.samples = {}
            self.create_project_dir()
            self.write_json()

    def create_project_dir(self):
        """
        Creates a project directory.
        """
        # Create directory for project
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def get_project_dict(self):
        project_dict = {"name": self.name,
                        "path": self.path,
                        "json_path": self.json_path,
                        "creation_datetime": self.creation_datetime,
                        "samples": self.samples}
        return project_dict

    def read_json(self, json_path):
        """
        Read in json file to assign class attributes.
        """
        # Read in json file
        f = open(json_path)
        project_dict = json.load(f)
        f.close()

        # Assign to class variables
        self.name = project_dict["name"]
        self.path = project_dict["path"]
        self.json_path = project_dict["json_path"]
        self.creation_datetime = project_dict["creation_datetime"]
        self.samples = project_dict["samples"]

    def write_json(self):
        """
        Function to write project information to a json file in the project
        dir.
        """
        with open(self.json_path, 'w') as f:
            json.dump(self.get_project_dict(), f)

    def add_sample(self, sample):
        """
        Add a sample to the project sample dictionary and update project json
        file.
        """
        self.samples[sample.name] = sample.json_path
        self.write_json()

    def remove_sample(self, s_name):
        """
        Remove sample data from project.
        """
        del self.samples[s_name]
        self.write_json()


class Sample():
    """
    Sample object.
    """

    def __init__(self, name=None, project=None, imgs=None, json_path=None):
        """
        Either initialises a new sample class and saves sample data to json, or
        inits directly from sample json file, specified by json_path.

        Args:
            name - sample name str
            project - project object for parent project
            json_path - absolute path to json file containing sample data to
            init from.
        """
        if json_path is not None:
            self.read_json(json_path)
            self.project = Project(json_path=self.project_json_path)
        else:
            self.name = name
            self.imgs = imgs
            self.project = project
            self.project_json_path = project.json_path
            self.path = F"{self.project.path}{self.name}/"
            self.json_path = F"{self.path}{self.name}.json"
            self.creation_datetime = datetime.today().strftime("%d-%m-%Y-%H:%M:%S")
            self.create_sample_dir()
            self.write_json()

            # Update parent project to include refs to sample json file
            project.add_sample(self)

    def create_sample_dir(self):
        """
        Creates a directory within the assigned project directory for sample
        data.
        """
        # Create directory for project
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def get_sample_dict(self):
        sample_dict = {"name": self.name,
                       "imgs": self.imgs,
                       "project_json_path": self.project_json_path,
                       "path": self.path,
                       "json_path": self.json_path,
                       "creation_datetime": self.creation_datetime}
        return sample_dict

    def read_json(self, json_path):
        """
        Read in json file to assign class attributes.
        """
        # Read in json file
        f = open(json_path)
        project_dict = json.load(f)
        f.close()

        # Assign to class variables
        self.name = project_dict["name"]
        self.imgs = project_dict["imgs"]
        self.project_json_path = project_dict["project_json_path"]
        self.path = project_dict["path"]
        self.json_path = project_dict["json_path"]
        self.creation_datetime = project_dict["creation_datetime"]

    def write_json(self):
        """
        Writes sample data to json file in sample directory.
        """
        with open(self.json_path, 'w') as f:
            json.dump(self.get_sample_dict(), f)

    def get_image_path(self, img_type):
        """
        Returns the path of a sample image, takes as argument image type to
        retrieve.
        """
        if img_type == "SD":
            return F"{self.path}{self.imgs['SD']}"
        if img_type == "IR":
            return F"{self.path}{self.imgs['IR']}"

    def delete_sample(self):
        """
        Delete all sample data.
        """
        shutil.rmtree(self.path)

    # def rename(self, name):
    #     """
    #     Update sample name. Calls save to project funciton with own project,
    #     then deletes original sample directory.
    #     """
    #     self.name = name
    #     reassign
    #     self.write_json()

    def save_to_project(self, project, name=None, delete=False):
        """
        Function to save sample to a new project.

        Args:
            name - new name for sample if rename required. If None, retains
            current name.
        """
        # Retain old sample details to copy images from / delete if needed
        prev_name = self.name
        prev_path = self.path
        prev_project = self.project

        # Assign name if sample needs renaming
        if name is not None:
            self.name = name

        # Reassign object vars, create sample folder + json in target project
        self.project = project
        self.project_json_path = project.json_path
        self.path = F"{self.project.path}{self.name}/"
        self.json_path = F"{self.path}{self.name}.json"
        self.create_sample_dir()
        self.write_json()

        # Copy images from previous project to target project
        for type, img in self.imgs.items():
            shutil.copy(F"{prev_path}{img}",
                        F"{self.path}{img}")

        # Add sample to target project data
        project.add_sample(self)

        # Delete old sample
        if delete is True:
            shutil.rmtree(prev_path)
            prev_project.remove_sample(prev_name)
