# pylint: disable=all
import pathlib
import pytest
import os

from uwtools.loaders import load_yaml
from uwtools.configure import Config

file_base = os.path.dirname(__file__)

def test_YAML_loader_loads_correctly():
    actual = load_yaml(pathlib.Path(os.path.join(file_base,"fixtures/simple.yaml"),parse=False))

    expected = {
        "scheduler": "slurm",
        "jobname": "abcd",
        "extra_stuff": 12345,
        "account": "user_account",
        "nodes": 1,
        "queue": "bos",
        "tasks_per_node": 4,
        "walltime": "00:01:00",
    }
    assert actual == expected


def test_YAML_loader_dot_notation():

    props = load_yaml(pathlib.Path(os.path.join(file_base,"fixtures/simple.yaml"), parse=False))

    expected = "abcd"
    actual = props.jobname
    assert actual == expected


def test_YAML_loader_parse_env():

    props = Config(pathlib.Path(os.path.join(file_base,"fixtures/experiment.yaml")))

    expected = os.environ.get('USER')
    actual = props.user
    assert actual == expected


def test_YAML_loader_update():

    props = Config(pathlib.Path(os.path.join(file_base,"fixtures/experiment.yaml")))
    props = Config(pathlib.Path(os.path.join(file_base,"fixtures/gfs.yaml")),props)

    expected =  "/home/myexpid/{{current_cycle}}"
    actual = props.datapath

    assert actual == expected

def test_YAML_loader_realtime_update():

    props = Config(pathlib.Path(os.path.join(file_base,"fixtures/experiment.yaml")))
    props = Config(pathlib.Path(os.path.join(file_base,"fixtures/gfs.yaml")),props)

    expected =  "/home/myexpid/10102022"
    actual = props.updated_datapath

    assert actual == expected