from typing import Dict

from foreman.parser import ParsedScenario
from foreman.profile_status import get_available_profiles
from foreman.profile_status import get_profile_state
from foreman.types import ForemanSnapshot
from foreman.types import LifecycleState
from foreman_msgs.msg import ForemanActivity
from foreman_msgs.msg import ProfileState

_STATE_TO_MSG = {
    None: ProfileState.UNDEFINED,
    LifecycleState.UNCONFIGURED: ProfileState.UNCONFIGURED,
    LifecycleState.INACTIVE: ProfileState.INACTIVE,
    LifecycleState.ACTIVE: ProfileState.ACTIVE,
}


def _build_profile_messages(
    snapshot: ForemanSnapshot,
    config: ParsedScenario,
):
    """Build ProfileState messages for every configured profile."""
    observed_states: Dict[str, LifecycleState] = {
        component.name: component.lifecycle_state
        for component in snapshot.components
    }

    available_profiles = get_available_profiles(
        config.profiles,
        set(observed_states.keys()),
    )

    messages = []

    for name, profile in config.profiles.items():
        msg = ProfileState()

        msg.name = name

        if name in available_profiles:
            msg.status = ProfileState.AVAILABLE
        else:
            msg.status = ProfileState.UNAVAILABLE

        state = get_profile_state(
            profile,
            observed_states,
        )

        msg.state = _STATE_TO_MSG[state]

        messages.append(msg)

    return messages


def build_foreman_activity(
    snapshot: ForemanSnapshot,
    config: ParsedScenario,
):
    """Build a ForemanActivity message."""
    msg = ForemanActivity()

    msg.profiles = _build_profile_messages(
        snapshot,
        config,
    )

    return msg
