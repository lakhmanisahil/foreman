from typing import Any, Dict, Set


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
