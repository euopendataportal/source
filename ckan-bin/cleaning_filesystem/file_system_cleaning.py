from __future__ import print_function
from logging.handlers import TimedRotatingFileHandler

import sys
import logging
import os
import glob
import shutil

log = logging.getLogger(__name__)

def main(parameters):
    log.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = TimedRotatingFileHandler('cleaning.log',when='midnight',  backupCount=30)
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    log.addHandler(fh)
    log.addHandler(ch)
    log.info("Initialization done.")
    if len(parameters) == 1:
        log.debug('found one parameter: ' + parameters[0])
        path_file = parameters[0]

    else:
        log.error("Invalid number of arguments! Put the path of the file")
        sys.exit(1)

    clean_file_system(path_file)
    # initialize(parameters[0])
    # log.info("Initialization done.")
    # log.info("Log level: " + log.getLevelName(log.getLogger("root").getEffectiveLevel()) + "\n")


def initialize(config_file_path):
    """
    Check the parameters and do some other initializations
    """


def clean_file_system(path):
    file = str(os.getcwd()) + '/' + path
    log.debug('start cleaning file system ' + file)
    if os.path.isfile(file) == False:
        log.error("The path given in parameter is not a file")
        sys.exit(1)

    try:
       
       with open(file) as f:
       
           try:
               for line in f:

                   line = line.lstrip()
                   line = line.replace('\n', '').replace('\r', '')
                   
                   if line.startswith('#') == False:
                       if  os.path.isdir(line):
                           shutil.rmtree(line, ignore_errors=True)
                       else:
                           files = [fi for fi in glob.glob(str(line)) if os.path.isfile(fi)]
                           for file2 in files:
                               os.remove(file2)

           except OSError as e:
               log.error(e.message)
           except :
               log.exception( 'unpredicted error')

    except :
       log.exception( 'unpredicted error')
	   
# Actually launch this module:
if __name__ == "__main__":
    main(sys.argv[1:])
