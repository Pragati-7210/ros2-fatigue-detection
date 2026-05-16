import rclpy
import json
from rclpy.node import Node
from std_msgs.msg import String


class SettingsNode(Node):

    def __init__(self):
        super().__init__('settings_node')

        # Publisher
        self.permissions_pub = self.create_publisher(
            String,
            '/permissions',
            10
        )

        # Default settings
        self.camera_enabled = True
        self.typing_enabled = True

        # Timer
        self.timer = self.create_timer(
            2.0,
            self.publish_permissions
        )

    def publish_permissions(self):

        if self.camera_enabled and self.typing_enabled:

            current_mode = "FULL_MONITORING"

        elif not self.camera_enabled and self.typing_enabled:

            current_mode = "PRIVACY_MODE"

        else:

            current_mode = "MINIMAL_MODE"

        permission_state = {
            "camera": self.camera_enabled,
            "typing": self.typing_enabled,
            "mode": current_mode
        }

        msg = String()
        msg.data = json.dumps(permission_state)

        self.permissions_pub.publish(msg)

        self.get_logger().info(
            f'Permissions: {permission_state}'
        )


def main(args=None):

    rclpy.init(args=args)

    node = SettingsNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()