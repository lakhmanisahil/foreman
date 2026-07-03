from pathlib import Path

from foreman.activity_message import build_foreman_activity
from foreman.parser import parse_yaml_file
from foreman.types import Component
from foreman.types import ComponentType
from foreman.types import ErrorSnapshot
from foreman.types import ForemanSnapshot
from foreman.types import LifecycleState
from foreman_msgs.msg import ProfileState

CONFIG = Path(__file__).parent / "test_meta_profiles_config.yaml"


def parsed():
    return parse_yaml_file(CONFIG)


def snapshot():
    return ForemanSnapshot(
        goal="running",
        ready=True,
        at_goal=True,
        error=ErrorSnapshot(
            is_error=False,
            category="",
            message="",
            components=[],
        ),
        components=[
            Component(
                "FrankaHardwareInterface",
                ComponentType.HARDWARE,
                LifecycleState.ACTIVE,
            ),
            Component(
                "kassow",
                ComponentType.HARDWARE,
                LifecycleState.ACTIVE,
            ),
            Component(
                "dummy_lifecycle_node",
                ComponentType.LIFECYCLE_NODE,
                LifecycleState.ACTIVE,
            ),
        ],
    )


def test_build_message_reports_active_available_profile():
    """An active and available profile is reported correctly."""

    msg = build_foreman_activity(
        snapshot(),
        parsed(),
    )

    base = next(
        profile
        for profile in msg.profiles
        if profile.name == "base"
    )

    assert base.status == ProfileState.AVAILABLE
    assert base.state == ProfileState.ACTIVE


def test_build_message_copies_engine_snapshot_fields():
    """The activity message copies the engine snapshot."""

    msg = build_foreman_activity(
        snapshot(),
        parsed(),
    )

    assert msg.current_goal == "running"
    assert msg.ready is True
    assert msg.at_goal is True

    assert msg.is_error is False
    assert msg.error_category == ""
    assert msg.error_message == ""
    assert msg.error_components == []


def test_build_message_reports_active_available_meta_profile():
    """An active and available meta-profile is reported correctly."""

    msg = build_foreman_activity(
        snapshot(),
        parsed(),
    )

    running = next(
        meta_profile
        for meta_profile in msg.meta_profiles
        if meta_profile.name == "running"
    )

    assert running.status == ProfileState.AVAILABLE
    assert running.state == ProfileState.ACTIVE
