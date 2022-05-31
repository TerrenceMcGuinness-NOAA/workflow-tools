#!/usr/bin/env python3
import pathlib
import os

from uwtools.yamlparser import YamlParser

#def test_yaml_parses_correctly():

file_base = os.path.join(os.path.dirname(__file__))
config = YamlParser(pathlib.Path(os.path.join(file_base,"fixtures/experiment.yaml")))

print("\n")
for key,value in config.items():
    print(key,value)
print("\n")

print(config.user)
print(config.generic_repos.url)