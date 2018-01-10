# check local user if it set up properly 
import sys
import os 
import config_env 
from rf.utils.sg import sg_utils
env = config_env.read()

def local_user(): 
	return os.environ(env.get('CONFIG'))

def sg_user(): 
	return sg_utils.sg.find('HumanUser', [], ['name', 'sg_localuser'])
