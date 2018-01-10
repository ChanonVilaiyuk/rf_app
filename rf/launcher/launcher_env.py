import os 
import sys
import json

class Config: 
    moduleDir = os.path.dirname(sys.modules[__name__].__file__)
    configFile = '%s/launcher_config.json' % moduleDir

def read(): 
    with open(Config.configFile) as configData: 
        config = json.load(configData)
        return config
    return dict()