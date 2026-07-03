from rclpy.node import Node
from rclpy.qos import DurabilityPolicy
from rclpy.qos import HistoryPolicy
from rclpy.qos import QoSProfile
from rclpy.qos import ReliabilityPolicy

from foreman.activity_message import build_foreman_activity
from foreman.engine import ForemanEngine
from foreman_msgs.msg import ForemanActivity


class RosActivityPublisher:
    """ROS 2 publisher for the current Foreman activity."""

    def __init__(self, node: Node, engine: ForemanEngine):
        self._node = node
        self._engine = engine
        self.logger_prefix = "Adapters.RosActivityPublisher:"

        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )

        self._publisher = self._node.create_publisher(
            ForemanActivity,
            "foreman/activity",
            qos_profile,
        )

        self._node.get_logger().info(
            f"{self.logger_prefix} Topic /foreman/activity is ready."
        )

    def publish(self):
        """Publish the current Foreman activity."""
        snapshot = self._engine.get_engine_snapshot()

        msg = build_foreman_activity(
            snapshot,
            self._engine.config,
        )

        msg.header.stamp = self._node.get_clock().now().to_msg()

        self._publisher.publish(msg)
