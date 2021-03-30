import os
from tex_py_gui.config import DirConfig


def get_p_names():
    """
    Function to look through project dir and get a list of all current project
    names.
    """
    # Get all project directories in main project dir and sort
    entries = os.scandir(DirConfig.project_dir)
    dirs = [e.name for e in entries if os.path.isdir(e)]
    dirs.sort(key=lambda d: d.lower())
    return dirs
