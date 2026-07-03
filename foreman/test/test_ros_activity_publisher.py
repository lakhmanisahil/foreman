from pathlib import Path
import unittest
from unittest import mock
from unittest.mock import Mock

import rclpy

from foreman.adapters.ros_activity_publisher import RosActivityPublisher
from foreman.parser import parse_yaml_file
from foreman.types import Component
from foreman.types import ComponentType
from foreman.types import ErrorSnapshot
from foreman.types import ForemanSnapshot
from foreman.types import LifecycleState
from foreman_msgs.msg import ProfileState

CONFIG = Path(__file__).parent / "test_meta_profiles_config.yaml"


def snapshot():
    """Build a snapshot representing a fully running system."""
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
            Component(
                "joint_state_broadcaster",
                ComponentType.CONTROLLER,
                LifecycleState.ACTIVE,
            ),
            Component(
                "kassow_joint_trajectory_controller",
                ComponentType.CONTROLLER,
                LifecycleState.ACTIVE,
            ),
            Component(
                "franka_joint_trajectory_controller",
                ComponentType.CONTROLLER,
                LifecycleState.ACTIVE,
            ),
        ],
    )


class TestRosActivityPublisher(unittest.TestCase):
    """Tests publishing Foreman activity."""

    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        self.node = rclpy.create_node("test_ros_activity_publisher")
        self.addCleanup(self.node.destroy_node)

        self.engine = Mock()
        self.engine.get_engine_snapshot.return_value = snapshot()
        self.engine.config = parse_yaml_file(CONFIG)

        self.publisher = RosActivityPublisher(
            node=self.node,
            engine=self.engine,
        )

    def test_publish_builds_and_publishes_activity_message(self):
        """Publishing builds a ForemanActivity message."""

        with mock.patch.object(
            self.publisher._publisher,
            "publish",
        ) as publish:

            self.publisher.publish()

        publish.assert_called_once()

        msg = publish.call_args.args[0]

        self.assertEqual(msg.current_goal, "running")
        self.assertTrue(msg.ready)
        self.assertTrue(msg.at_goal)

        base = next(
            profile
            for profile in msg.profiles
            if profile.name == "base"
        )

        self.assertEqual(
            base.status,
            ProfileState.AVAILABLE,
        )

        self.assertEqual(
            base.state,
            ProfileState.ACTIVE,
        )


if __name__ == "__main__":
    unittest.main()
