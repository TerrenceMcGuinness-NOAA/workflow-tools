"""
Loads yaml configuration files as python Configure objects

https://pyyaml.org/wiki/PyYAMLDocumentation
"""

from uwtools.nameddict import NamedDict
from uwtools.template import Template
from uwtools.loaders import load_yaml

class Config(NamedDict):

    def __init__(self, config_file=None, data=None, parse=True):
        super().__init__()
        if config_file is not None:
            config = load_yaml(config_file, False)
        if ( data is not None ) and ( config  is not None):
            if parse == True:
                config = Template.replace_from_environment(config)
                config = Template.replace_with_dependencies(config,data)
        elif config is not None:
            if parse is True:
                config = Template.replace_from_environment(config)
                config = Template.replace_with_dependencies(config,config)

        self.update(self._configure(config))

    def _configure(self, config):
        for key, value in config.items():
            if isinstance(value, dict):
                config[key] = NamedDict(value)
                self._configure(value)
            elif isinstance(value, list):
                for i, v in enumerate(value):
                    if isinstance(v, dict):
                        value[i] = NamedDict(v)
                        self._configure(v)
        return config