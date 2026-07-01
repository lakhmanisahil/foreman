from pathlib import Path

from foreman.parser import parse_yaml_file
from foreman.profile_status import get_available_meta_profiles
from foreman.profile_status import get_available_profiles

CONFIG = Path(__file__).parent / "test_meta_profiles_config.yaml"


def parsed():
    return parse_yaml_file(CONFIG)


def test_base_profile_is_available():
    scenario = parsed()

    observed = {
        "FrankaHardwareInterface",
        "kassow",
        "dummy_lifecycle_node",
    }

    available = get_available_profiles(
        scenario.profiles,
        observed,
    )

    assert "base" in available


def test_base_profile_is_unavailable_when_a_required_component_is_missing():
    scenario = parsed()

    observed = {
        "FrankaHardwareInterface",
        "dummy_lifecycle_node",
    }

    available = get_available_profiles(
        scenario.profiles,
        observed,
    )

    assert "base" not in available


def test_profile_is_available_when_extra_components_are_present():
    scenario = parsed()

    observed = {
        "FrankaHardwareInterface",
        "kassow",
        "dummy_lifecycle_node",
        "joint_state_broadcaster",
        "camera",
    }

    available = get_available_profiles(
        scenario.profiles,
        observed,
    )

    assert "base" in available


def test_broadcaster_profile_is_available():
    scenario = parsed()

    observed = {
        "joint_state_broadcaster",
    }

    available = get_available_profiles(
        scenario.profiles,
        observed,
    )

    assert "broadcaster" in available


def test_broadcaster_profile_is_unavailable():
    scenario = parsed()

    observed = {
        "FrankaHardwareInterface",
        "kassow",
    }

    available = get_available_profiles(
        scenario.profiles,
        observed,
    )

    assert "broadcaster" not in available


def test_trajectory_profile_is_available():
    scenario = parsed()

    observed = {
        "kassow_joint_trajectory_controller",
        "franka_joint_trajectory_controller",
    }

    available = get_available_profiles(
        scenario.profiles,
        observed,
    )

    assert "trajectory" in available


def test_trajectory_profile_is_unavailable():
    scenario = parsed()

    observed = {
        "kassow_joint_trajectory_controller",
    }

    available = get_available_profiles(
        scenario.profiles,
        observed,
    )

    assert "trajectory" not in available


def test_idle_meta_profile_is_available():
    scenario = parsed()

    available_profiles = {
        "base",
        "broadcaster",
        "trajectory",
    }

    available = get_available_meta_profiles(
        scenario.meta_profiles,
        available_profiles,
    )

    assert "idle" in available
