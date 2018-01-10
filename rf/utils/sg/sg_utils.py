import sys
import os
import logging

logger = logging.getLogger(__name__)

import config
from shotgun_api3 import Shotgun

# connection to server
server = config.server
script = config.script
id = config.id
sg = Shotgun(server, script, id)
# sg = None

def init_key(inputKey): 
	script, id = config.get_key(inputKey)
	global sg
	sg = Shotgun(server, script, id)