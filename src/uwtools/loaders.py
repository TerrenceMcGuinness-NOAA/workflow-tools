"""
Loads yaml configuration files as python objects

https://pyyaml.org/wiki/PyYAMLDocumentation
"""

import pathlib
from yaml import load, YAMLError

try:
    from yaml import CLoader as BaseLoader
except ImportError:
    from yaml import Loader

from uwtools.nameddict import NamedDict
from uwtools.template import Template

def load_yaml(_path: pathlib.Path, parse=True):
    with open(_path, "r") as _file:
        try:
            props = NamedDict(load(_file, Loader=BaseLoader))
        except YAMLError as exc:
            print(exc)

        if parse is True:
            props = Template.replace_from_environment(props)
            props = Template.replace_with_dependencies(props,props)

        return props