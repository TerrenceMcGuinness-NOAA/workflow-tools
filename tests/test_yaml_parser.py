# pylint: disable=all
import pathlib
import pytest
import os

from uwtools.configuration import Configuration

#def test_yaml_parses_correctly():

file_base = os.path.join(os.path.dirname(__file__))
config = Configuration(pathlib.Path(os.path.join(file_base,"fixtures/experiment.yaml")))

print("\n")
for key,value in config.items():
    print(key,value)
print("\n")
print(config.user)
print(config.generic_repos)

for each in config.generic_repos:
    for all in each:
        print(all)