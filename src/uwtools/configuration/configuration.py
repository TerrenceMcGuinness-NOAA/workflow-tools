from calendar import c
import os
from tokenize import Name
import yaml
import collections

from ..template import Template
from ..nameddict import NamedDict
from ..template import TemplateConstants

class Configuration(NamedDict):
    """
        A class that reads a yaml file into a Configuration object
    """
    def __init__(self, config_file, schema_path='.', schema_name=None ):
        super().__init__()
        self.source = os.path.abspath(config_file)
        with open(os.path.abspath(config_file)) as f:
            #config = NamedDict(yaml.load(f, Loader=yaml.FullLoader))
            try:
                config = yaml.load(f, Loader=yaml.FullLoader)
            except yaml.YAMLError as exc:
                print(exc)
            if config is None:
                config = {}
            config = Template.substitute_structure_from_environment(config)
            config = Template.substitute_with_dependencies(config,config,TemplateConstants.DOLLAR_PARENTHESES)
        self.update(NamedDict(config))