from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any, Dict, List, Set

import yaml

from foreman.types import Component
from foreman.types import ComponentType
from foreman.types import ControllerDependencyRule
from foreman.types import LifecycleState
from foreman.types import SystemGoal

# TODO: Once we settle on a config model
# TODO: Bulletproof this config parsing once we settle on one
# TODO: reconsider naming, for example ParsedScenario
# TODO: Rethink parsing output structure dataclass


@dataclass
class ParsedScenario:
    """Complete parsed scenario configuration."""

    hardware: List[str]
    dependency_rules: List[ControllerDependencyRule]
    goals: Dict[str, SystemGoal]
    lifecycle_nodes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tracked_components: Set[str] = field(default_factory=set)
    profiles: Dict[str, Any] = field(default_factory=dict)
    meta_profiles: Dict[str, Any] = field(default_factory=dict)


def parse_state_string(state_str: str) -> LifecycleState:
    """Convert YAML state string to LifecycleState enum."""
    state_mapping = {
        'unconfigured': LifecycleState.UNCONFIGURED,
        'inactive': LifecycleState.INACTIVE,
        'active': LifecycleState.ACTIVE,
        'finalized': LifecycleState.FINALIZED,
    }
    normalized = state_str.lower()
    if normalized not in state_mapping:
        raise ValueError(f"Unknown state: {state_str}")
    return state_mapping[normalized]


def parse_yaml_file(file_path: Path) -> ParsedScenario:
    """Parse a scenario YAML file into a ParsedScenario object."""
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)

    if data is None:
        raise ValueError("Empty YAML file")

    meta_profiles = data["meta_profiles"]
    profiles = data["profiles"]

    hardware_names = []
    lifecycle_node_names = []

    # Dependencies are inferred at runtime from the controller_manager
    dependency_rules: List[ControllerDependencyRule] = []

    goals = {}

    for meta_profile_name, profile_states in meta_profiles.items():
        hw_goals = []
        ctrl_goals = []
        lc_goals = []

        for profile_name, profile_config in profile_states.items():
            if profile_name not in profiles:
                raise ValueError(
                    f"Unknown profile '{profile_name}' referenced by meta-profile '{meta_profile_name}'"
                )

            if "state" not in profile_config:
                raise ValueError(
                    f"Profile '{profile_name}' in meta-profile "
                    f"'{meta_profile_name}' is missing a 'state' field."
                )

            profile_state = parse_state_string(profile_config["state"])
            profile = profiles[profile_name]

            for controller in profile.get("controllers", []):
                ctrl_goals.append(
                    Component(
                        controller,
                        ComponentType.CONTROLLER,
                        profile_state,
                    )
                )

            for hardware in profile.get("hardware", []):
                hw_goals.append(
                    Component(
                        hardware,
                        ComponentType.HARDWARE,
                        profile_state,
                    )
                )

                if hardware not in hardware_names:
                    hardware_names.append(hardware)

            for lifecycle_node in profile.get("lifecycle_nodes", []):
                lc_goals.append(
                    Component(
                        lifecycle_node,
                        ComponentType.LIFECYCLE_NODE,
                        profile_state,
                    )
                )

                if lifecycle_node not in lifecycle_node_names:
                    lifecycle_node_names.append(lifecycle_node)

        goals[meta_profile_name] = SystemGoal(
            name=meta_profile_name,
            hardware_goals=hw_goals,
            controller_goals=ctrl_goals,
            lifecycle_node_goals=lc_goals,
        )

    metadata = {}
    known_keys = {"profiles", "meta_profiles"}

    for key, value in data.items():
        if key not in known_keys:
            metadata[key] = value

    tracked_components = set(hardware_names + lifecycle_node_names)
    for goal in goals.values():
        tracked_components.update(c.name for c in goal.hardware_goals)
        tracked_components.update(c.name for c in goal.controller_goals)
        tracked_components.update(c.name for c in goal.lifecycle_node_goals)

    return ParsedScenario(
        hardware=hardware_names,
        lifecycle_nodes=lifecycle_node_names,
        dependency_rules=dependency_rules,
        goals=goals,
        metadata=metadata,
        tracked_components=tracked_components,
        profiles=profiles,
        meta_profiles=meta_profiles
    )
