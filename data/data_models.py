"""
Data models for all objects (projects, samples etc).
"""

import os
import json
from datetime import datetime
from tex_py_gui.config import DirConfig


class Project():
    """
    Project class. If calling init with p_json, skips standard initialisaiton
    and initialises from json file.
    """

    def __init__(self, name, p_json=None):
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
                        "creation_date": self.creation_date}
        return project_dict

    def write_json(self):
        """
        Function to write project information to a json file in the project
        dir.
        """
        json_path = F"{self.path}{self.name}.json"
        with open(json_path, 'w') as f:
            json.dump(self.get_project_dict(), f)
