import os
import json
from warnings import warn

#     The location of this file can be specified by the NIOC_CONFIG_FILE
#     environment variable (which the user needs to set himself/herself.
#     If there is no such environment variable, the filepath "~/.nioc_config.json" will be used.
DFLT_CONFIG_FILE = os.path.expanduser('~/.nioc_config.json')
config_file = os.getenv('NIOC_CONFIG_FILE', DFLT_CONFIG_FILE)

try:
    config_dict = json.load(open(config_file))
except FileNotFoundError:
    warn("The config file wasn't found: {}".format(config_file))
    warn("--> Make one or some functionalities might not be available or work properly.")
    config_dict = {}  #
except json.JSONDecodeError as e:
    warn("The config json had some problems being decoded: {}".format(config_file))
    warn("Error said: {}".format((e)))
    warn("--> Make one or some functionalities might not be available or work properly.")
    config_dict = {}  #

json_deserializers_dict = {
    'app_root': os.path.expanduser  # to allow a user to specify a path with a "~" prefix
}

# transforming the config_dict
for k, deserializer_func in json_deserializers_dict.items():
    if k in config_dict:
        config_dict[k] = deserializer_func(config_dict[k])

# In order to express more complicated python objects, one can specify key-val pairs in the module's
# json_deserializers_dict. The values there are functions that will be applied to the json's values
# (but not the default_dict values) to transform it to the desired python object.


#  An additional default_dict is specified in this module and will be used if a key is not present in config file.
default_dict = {

}

config_dict = dict(default_dict, **config_dict)  # adding defaults (but config_dict takes precedence)

# config is an object containing the configurations/constants/etc. as attributes.
config = type('_config', (object,), config_dict)  # an object containing the configurations/constants/etc. as attributes

__all__ = [config, config_dict]
