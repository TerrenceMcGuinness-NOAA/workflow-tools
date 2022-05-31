import os
import yaml

from ..template import Template
from ..nameddict import NamedDict

class YamlParser(NamedDict):
    """
        A class that reads a yaml file into a Configuration object
    """
    def __init__(self, config_file, schema_path='.', schema_name=None ):
        super().__init__()
        self.source = os.path.abspath(config_file)
        with open(os.path.abspath(config_file)) as f:
            try:
                config = yaml.load(f, Loader=yaml.FullLoader)
                #config = NamedDict(yaml.load(f, Loader=yaml.FullLoader))
            except yaml.YAMLError as exc:
                print(exc)
            if config is None:
                config = {}
            config = Template.replace_structure_from_environment(config)
            config = Template.replace_with_dependencies(config,config)
        self.update(config)
        #self.update(NamedDict(config))