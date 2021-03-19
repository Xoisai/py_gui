import os
from kivy.config import Config

BASEDIR = os.path.abspath(os.path.dirname(__file__))

# Graphics Params
Config.set("graphics", "width", "1024")
Config.set("graphics", "height", "600")


class DirConfig():

    project_dir = BASEDIR + "/projects/"
    kv_dir = BASEDIR + "/kv/"
