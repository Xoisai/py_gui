"""
Data models for all objects (projects, samples etc).
"""

import os
import json
from datetime import datetime
from tex_py_gui.config import DirConfig


class Project():
    """
    Project class. If calling init with json_path, skips standard initialisaiton
    and initialises from json file.
    """

    def __init__(self, name=None, json_path=None):
        if json_path is not None:
            self.read_json(json_path)
        else:
            self.name = name
            self.path = F"{DirConfig.project_dir}{name}/"
            self.creation_date = datetime.today().strftime("%Y-%m-%d-%H:%M:%S")
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
                        "creation_date": self.creation_date}
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
        self.creation_date = project_dict["creation_date"]

    def write_json(self):
        """
        Function to write project information to a json file in the project
        dir.
        """
        json_path = F"{self.path}{self.name}.json"
        with open(json_path, 'w') as f:
            json.dump(self.get_project_dict(), f)
