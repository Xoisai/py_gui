import os
from kivy.config import Config

BASEDIR = os.path.abspath(os.path.dirname(__file__))

# Graphics Params
# Config.set("graphics", "width", "1024")
# Config.set("graphics", "height", "600")
Config.set('graphics', 'fullscreen', 1)


class DirConfig():

    runtype = "pi"
    file_dir = BASEDIR + "/filesys/"
    project_dir = file_dir + "projects/"
    temp_dir = file_dir + "temp/"
    kv_dir = BASEDIR + "/kv/"
    temp_project_json = file_dir + "temp/temp.json"

class ModelConfig():

    model_path = "/home/pi/IR_modules/demo/models/aw_demo_int8.tflite"
