from rclpy.node import Node

from foreman.engine import ForemanEngine
from foreman.profile_status import get_available_meta_profiles
from foreman.profile_status import get_available_profiles
from foreman_msgs.srv import ListProfiles


class RosListProfilesServer:
    """ROS 2 service to list profiles and meta-profiles."""

    def __init__(
        self,
        node: Node,
        engine: ForemanEngine,
    ):
        self._node = node
        self._engine = engine

        self.logger_prefix = "Adapters.RosListProfilesServer:"

        self._srv = self._node.create_service(
            ListProfiles,
            "foreman/list_profiles",
            self._handle_list_profiles,
            callback_group=self._node.callback_group_services,
        )

        self._node.get_logger().info(
            f"{self.logger_prefix} Service /foreman/list_profiles is ready."
        )

    def _handle_list_profiles(
        self,
        request,
        response,
    ):
        profiles = self._engine.config.profiles
        meta_profiles = self._engine.config.meta_profiles

        snapshot = self._engine.get_engine_snapshot()

        observed_components = {
            component.name
            for component in snapshot.components
        }

        available_profiles = get_available_profiles(
            profiles,
            observed_components,
        )

        available_meta_profiles = get_available_meta_profiles(
            meta_profiles,
            available_profiles,
        )

        if request.filter == request.ALL:
            response.profiles = list(profiles.keys())
            response.meta_profiles = list(meta_profiles.keys())

        elif request.filter == request.AVAILABLE:
            response.profiles = list(available_profiles)
            response.meta_profiles = list(available_meta_profiles)

        return response
