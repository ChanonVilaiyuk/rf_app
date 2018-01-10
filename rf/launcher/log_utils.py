import logging
import os, sys
from datetime import datetime

# logRoot = '%s/logs' % os.environ.get('RFSCRIPT', 'D:/rftool')
logRoot = 'O:/logs'
logExt = 'log'

def name(toolName, user, createDir=True):
	date = str(datetime.now()).split(' ')[0]
	# userName = mc.optionVar(q='PTuser')
	userName = user
	logDir = '%s/%s/%s/%s' % (logRoot, date, toolName, userName)
	logName = '%s_%s_%s.%s' % (toolName, userName, date, logExt)

	if createDir:
		if not os.path.exists(logDir):
			os.makedirs(logDir)

	return '%s/%s' % (logDir, logName)

def init_logger(logFile):
	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)

	for each in logger.handlers[::-1] :
		if type(each).__name__ == 'StreamHandler':
			logger.removeHandler(each)

		if type(each).__name__== 'FileHandler':
			logger.removeHandler(each)
			each.flush()
			each.close()

	# create file handler which logs even debug messages
	fh = logging.FileHandler(logFile)
	fh.setLevel(logging.DEBUG)
	# create console handler with a higher log level
	ch = logging.StreamHandler()
	ch.setLevel(logging.INFO)
	# create formatter and add it to the handlers
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	fh.setFormatter(formatter)
	ch.setFormatter(formatter)
	# add the handlers to the logger
	logger.addHandler(fh)
	logger.addHandler(ch)

	return logger