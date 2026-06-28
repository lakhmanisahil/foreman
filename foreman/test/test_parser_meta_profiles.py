from pathlib import Path

from foreman.parser import parse_yaml_file

CONFIG = Path(__file__).parent.parent / "config" / "meta_profiles_config.yaml"


def test_meta_profiles_become_goals():
    parsed = parse_yaml_file(CONFIG)

    assert set(parsed.goals.keys()) == {
        "full_active",
        "sensing_only",
        "all_down",
    }
