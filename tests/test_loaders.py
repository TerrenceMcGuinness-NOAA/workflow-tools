# pylint: disable=all
import pathlib
import pytest
import os

from uwtools.loaders import load_yaml

file_base = os.path.dirname(__file__)

def test_yaml_loader_loads_correctly():
    actual = load_yaml(pathlib.Path(os.path.join(file_base,"fixtures/simple.yaml"),parse=False))

    expected = {
        "scheduler": "slurm",
        "jobname": "abcd",
        "extra_stuff": 12345,
        "account": "user_account",
        "nodes": 1,
        "queue": "bos",
        "tasks_per_node": 4,
        "walltime": "00:01:00"
        }
    assert actual == expected


def test_loader_dot_notation():

    props = load_yaml(pathlib.Path(os.path.join(file_base,"fixtures/simple.yaml"), parse=False))

    expected = "abcd"
    actual = props.jobname

    assert actual == expected

def test_YAML_loader_parse_env():

    props = load_yaml(pathlib.Path(os.path.join(file_base,"fixtures/experiment.yaml"), parse=True))

    expected = os.environ.get('USER')
    actual = props.user

    assert actual == expected