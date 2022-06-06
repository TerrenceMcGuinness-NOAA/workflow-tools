import yaml
from .nice_dict import NiceDict
from .language import stringify


class YAMLFile(NiceDict):

    """
        Reads a YAML file as a NiceDict and recursively converts
        nested dictionaries into NiceDict.
        Provides a way of saving the dictionary issued from the yaml file, after modification or not.
    """

    def __init__(self, config_file=None, data=None):
        super().__init__()
        if config_file is not None:
            with open(config_file) as f:
                config = yaml.load(f, Loader=yaml.BaseLoader)
        else:
            config = data
        if config is not None:
            self.update(self._configure(config))

    def _configure(self, config):
        for key, value in config.items():
            if isinstance(value, dict):
                config[key] = NiceDict(value)
                self._configure(value)
            elif isinstance(value, list):
                for i, v in enumerate(value):
                    if isinstance(v, dict):
                        value[i] = NiceDict(v)
                        self._configure(v)
        return config

    def save(self, target):
        with open(target, 'w') as f:
            # specifies a wide file so that long strings are on one line.
            yaml.dump(stringify(self), f, width=100000)
        return target

    def dump(self):
        return yaml.dump(stringify(self), width=100000)
