import os
activate_this = os.path.join('/applications/ecodp/users/ecodp/ckan/ecportal/bin/activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

from paste.deploy import loadapp
#config_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'development.ini')
config_filepath = os.path.join('/applications/ecodp/users/ecodp/ckan/conf/ecportal.ini')
from paste.script.util.logging_config import fileConfig
fileConfig(config_filepath)
application = loadapp('config:%s' % config_filepath)