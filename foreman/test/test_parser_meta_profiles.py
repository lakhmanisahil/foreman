from pathlib import Path

from foreman.parser import parse_yaml_file

CONFIG = Path(__file__).parent / "test_meta_profiles_config.yaml"


def parsed():
    return parse_yaml_file(CONFIG)


def test_profiles_are_preserved():
    scenario = parsed()

    assert set(scenario.profiles.keys()) == {
        "base",
        "broadcaster",
        "trajectory",
    }


def test_meta_profiles_are_preserved():
    scenario = parsed()

    assert set(scenario.meta_profiles.keys()) == {
        "idle",
        "broadcast_only",
        "running",
    }
