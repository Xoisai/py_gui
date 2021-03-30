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
    Project class. If calling init with json_path, skips standard
    initialisaiton and initialises from json file.
    """

    def __init__(self, name=None, json_path=None):
        if json_path is not None:
            self.read_json(json_path)
        else:
            self.name = name
            self.path = F"{DirConfig.project_dir}{name}/"
            self.json_path = F"{self.path}{self.name}.json"
            self.creation_date = datetime.today().strftime("%Y-%m-%d-%H:%M:%S")
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
                        "creation_date": self.creation_date,
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
        self.creation_date = project_dict["creation_date"]
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


class Sample():
    """
    Sample class. If calling init with json_path, skips standard
    initialisaiton and instantiates from json file.
    """

    def __init__(self, name=None, project=None, imgs=None, json_path=None):
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
            self.creation_date = datetime.today().strftime("%Y-%m-%d-%H:%M:%S")
            self.create_sample_dir()
            self.add_images()
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

    def add_images(self):
        """
        Transfers temp storage of images to permanent storage in project dir
        and renames to given name, then updates imgs class variable.
        """
        for type, img in self.imgs.items():
            shutil.move(F"{DirConfig.temp_dir}{img}",
                        F"{self.path}{type}-{self.name}.png")
            self.imgs[type] = F"{type}-{self.name}.png"

    def get_sample_dict(self):
        sample_dict = {"name": self.name,
                       "imgs": self.imgs,
                       "project_json_path": self.project_json_path,
                       "path": self.path,
                       "json_path": self.json_path,
                       "creation_date": self.creation_date}
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
        self.creation_date = project_dict["creation_date"]

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
