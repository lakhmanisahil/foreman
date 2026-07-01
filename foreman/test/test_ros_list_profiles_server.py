import unittest
from unittest.mock import Mock

import rclpy
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup

from foreman.adapters.ros_list_profiles_server import RosListProfilesServer
from foreman.types import Component
from foreman.types import ComponentType
from foreman.types import ErrorSnapshot
from foreman.types import ForemanSnapshot
from foreman.types import LifecycleState
from foreman_msgs.srv import ListProfiles


class TestRosListProfilesServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):

        self.node = rclpy.create_node("test_list_profiles")
        self.node.callback_group_services = MutuallyExclusiveCallbackGroup()
        self.addCleanup(self.node.destroy_node)
        self.engine = Mock()
        self.engine.config = Mock()

        self.engine.config.profiles = {
            "base": {},
            "broadcaster": {},
            "trajectory": {},
        }

        self.engine.config.meta_profiles = {
            "running": {},
            "idle": {},
        }

        self.engine.get_engine_snapshot.return_value = ForemanSnapshot(
            goal="None",
            ready=True,
            at_goal=True,
            error=ErrorSnapshot(
                is_error=False,
                category="None",
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

        self.server = RosListProfilesServer(
            self.node,
            self.engine,
        )

    def test_all_filter_returns_all_profiles_and_meta_profiles(self):

        request = ListProfiles.Request()
        request.filter = request.ALL
        response = ListProfiles.Response()

        response = self.server._handle_list_profiles(
            request,
            response,
        )

        self.assertEqual(
            set(response.profiles),
            {
                "base",
                "broadcaster",
                "trajectory",
            },
        )

        self.assertEqual(
            set(response.meta_profiles),
            {
                "idle",
                "running",
            },
        )
