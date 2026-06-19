import unittest
import rclpy
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from foreman.adapters.controller_manager_service_caller import ControllerManagerServiceCaller


class TestControllerManagerNamespacing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def _make_node(self, namespace=None):
        node = rclpy.create_node('foreman_node', namespace=namespace)
        node.callback_group_services = MutuallyExclusiveCallbackGroup()
        self.addCleanup(node.destroy_node)
        return node

    def _resolved_switch_name(self, node):
        caller = ControllerManagerServiceCaller(node, 'controller_manager')
        built = caller._client_switch_controller.srv_name      # name the ADAPTER built
        return node.resolve_service_name(built)                # resolve it under the namespace

    def test_global(self):
        node = self._make_node()
        self.assertEqual(self._resolved_switch_name(node),
                         '/controller_manager/switch_controller')

    def test_single_namespace(self):
        node = self._make_node(namespace='/rrbot')
        self.assertEqual(self._resolved_switch_name(node),
                         '/rrbot/controller_manager/switch_controller')

    def test_double_namespace(self):
        node = self._make_node(namespace='/factory/rrbot')
        self.assertEqual(self._resolved_switch_name(node),
                         '/factory/rrbot/controller_manager/switch_controller')

if __name__ == '__main__':
    unittest.main()
