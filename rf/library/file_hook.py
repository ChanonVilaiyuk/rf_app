import os
import sys 
from rf.utils import file_utils
from rftool.utils import path_info


class Path: 
    sep = '/'

class ProjectConfig: 
    root = os.environ.get('RFPROJECT')
    asset = 'asset'
    shot = 'scene'
    lib = 'lib'


def get_project(): 
    info = list()
    projects = file_utils.listFolder(ProjectConfig.root)

    for project in projects: 
        info.append({'name': project, 'id': 0, 'sg_project_path': ProjectConfig.root})

    return info


def get_type(root, project): 
    typePath = Path.sep.join([root, project, ProjectConfig.asset])
    types = file_utils.listFolder(typePath)
    return types 


def get_subtypes(project, type): 
    root = project.get('sg_project_path')
    projectName = project.get('name')
    subTypePath = Path.sep.join([root, projectName, ProjectConfig.asset, type])
    subTypes = file_utils.listFolder(subTypePath)
    return subTypes


def get_assets(project, type, subtype): 
    root = project.get('sg_project_path')
    projectName = project.get('name')
    assetPath = Path.sep.join([root, projectName, ProjectConfig.asset, type, subtype])
    assets = file_utils.listFolder(assetPath)
    entities = []

    for asset in assets: 
        entity = path_info.PathInfo(Path.sep.join([assetPath, asset, ProjectConfig.lib]))
        entities.append(entity)
    
    return entities
