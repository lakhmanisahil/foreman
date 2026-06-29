from pathlib import Path

import pytest

from foreman.parser import parse_yaml_file
from foreman.types import LifecycleState

CONFIG = Path(__file__).parent.parent / "config" / "meta_profiles_config.yaml"


def _states_by_name(components):
    return {c.name: c.lifecycle_state for c in components}


def test_meta_profiles_become_goals():
    parsed = parse_yaml_file(CONFIG)

    assert set(parsed.goals.keys()) == {
        "full_active",
        "sensing_only",
        "all_down",
    }


def test_profile_state_applied_to_every_component():
    goal = parse_yaml_file(CONFIG).goals["full_active"]

    ctrl = _states_by_name(goal.controller_goals)
    hw = _states_by_name(goal.hardware_goals)
    lc = _states_by_name(goal.lifecycle_node_goals)

    assert ctrl["forward_position_controller"] == LifecycleState.ACTIVE
    assert ctrl["joint_state_broadcaster"] == LifecycleState.ACTIVE

    assert hw["RRBot"] == LifecycleState.ACTIVE

    assert lc["dummy_lifecycle_node"] == LifecycleState.ACTIVE


def test_hardware_and_lifecycle_nodes_derived_from_profiles():
    parsed = parse_yaml_file(CONFIG)

    assert parsed.hardware == ["RRBot"]
    assert parsed.lifecycle_nodes == ["dummy_lifecycle_node"]


def test_tracked_components_cover_all_profile_components():
    parsed = parse_yaml_file(CONFIG)

    assert parsed.tracked_components == {
        "forward_position_controller",
        "joint_state_broadcaster",
        "RRBot",
        "dummy_lifecycle_node",
    }


def test_missing_profile_reference_raises(tmp_path):
    config = tmp_path / "missing_profile.yaml"

    config.write_text(
        "profiles:\n"
        "  motion:\n"
        "    controllers: [controller]\n"
        "\n"
        "meta_profiles:\n"
        "  running:\n"
        "    missing_profile:\n"
        "      state: active\n"
    )

    with pytest.raises(ValueError):
        parse_yaml_file(config)


def test_missing_profile_state_raises(tmp_path):
    config = tmp_path / "missing_state.yaml"

    config.write_text(
        "profiles:\n"
        "  motion:\n"
        "    controllers: [controller]\n"
        "\n"
        "meta_profiles:\n"
        "  running:\n"
        "    motion: {}\n"
    )

    with pytest.raises(ValueError):
        parse_yaml_file(config)
