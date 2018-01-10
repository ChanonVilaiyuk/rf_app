# using shotgun for database 
import os
import sys
import config 
from shotgun_api3 import Shotgun
from rf.utils import file_utils


# connection to server
script, id = config.get_key('library')
server = config.server
sg = Shotgun(server, script, id)

class Path: 
    sep = '/'

class ProjectConfig: 
    root = os.environ.get('RFPROJECT')
    asset = 'asset'
    shot = 'scene'


def get_project(): 
    """ get active project """
    filters = [['sg_status', 'is', 'Active']]
    fields = ['name', 'id', 'sg_project_path']
    return sg.find('Project', filters, fields)


def get_type(root, project): 
    typePath = Path.sep.join([root, project, ProjectConfig.asset])
    types = file_utils.listFolder(typePath)
    return types 

def get_assets(project, assetType): 
    filters = [['project', 'is', project], ['sg_asset_type', 'is', assetType]]
    fields = ['code', 'sg_asset_type', 'sg_subtype', 'id']
    return sg.find('Asset', filters, fields)
