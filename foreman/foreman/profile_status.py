from typing import Any, Dict, Optional, Set

from foreman.parser import parse_state_string
from foreman.types import LifecycleState


def get_available_profiles(
    profiles: Dict[str, Any],
    observed_components: Set[str],
) -> Set[str]:
    """Return the names of all available profiles.

    A profile is available when all of its required controllers, hardware,
    and lifecycle nodes are present in the observed component set.
    """
    available_profiles = set()

    for profile_name, profile_config in profiles.items():
        required_components = set()

        required_components.update(profile_config.get("controllers", []))
        required_components.update(profile_config.get("hardware", []))
        required_components.update(profile_config.get("lifecycle_nodes", []))

        if required_components.issubset(observed_components):
            available_profiles.add(profile_name)

    return available_profiles


def get_available_meta_profiles(
    meta_profiles: Dict[str, Any],
    available_profiles: Set[str],
) -> Set[str]:
    """Return the names of available meta-profiles.

    A meta-profile is available when all of its referenced profiles are
    available.
    """
    available_meta_profiles = set()

    for meta_profile_name, meta_profile_config in meta_profiles.items():

        required_profiles = set(meta_profile_config.keys())

        if required_profiles.issubset(available_profiles):
            available_meta_profiles.add(meta_profile_name)

    return available_meta_profiles


def get_profile_state(
    profile: Dict[str, Any],
    observed_states: Dict[str, LifecycleState],
) -> Optional[LifecycleState]:
    """Return the lifecycle state shared by a profile.

    Returns None when any required component is not observed.
    """
    required_components = set()

    required_components.update(profile.get("controllers", []))
    required_components.update(profile.get("hardware", []))
    required_components.update(profile.get("lifecycle_nodes", []))

    states = set()

    for component_name in required_components:
        if component_name not in observed_states:
            return None

        states.add(observed_states[component_name])

    if len(states) == 1:
        return next(iter(states))

    return None


def get_meta_profile_state(
    meta_profile: Dict[str, Any],
    profiles: Dict[str, Any],
    observed_states: Dict[str, LifecycleState],
) -> LifecycleState:
    """Return the state of a meta-profile."""
    for profile_name, target in meta_profile.items():

        target_state = parse_state_string(target["state"])

        actual_state = get_profile_state(
            profiles[profile_name],
            observed_states,
        )

        if actual_state != target_state:
            return LifecycleState.INACTIVE

    return LifecycleState.ACTIVE
