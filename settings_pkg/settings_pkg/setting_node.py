import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json


class SettingsNode(Node):

    def __init__(self):
        super().__init__('settings_node')

        # Publisher
        self.publisher_ = self.create_publisher(
            String,
            '/settings',
            10
        )

        # Timer
        self.timer = self.create_timer(
            2.0,
            self.publish_settings
        )

        # Default settings
        self.camera_enabled = True
        self.typing_enabled = False

        self.get_logger().info(
            "Settings Node has started 🚀"
        )

    def publish_settings(self):

        msg = String()

        # Privacy mode labels
        if self.camera_enabled and self.typing_enabled:
            current_mode = "FULL_MONITORING"

        elif not self.camera_enabled and self.typing_enabled:
            current_mode = "PRIVACY_MODE"

        else:
            current_mode = "MINIMAL_MODE"

        data = {
            "camera": self.camera_enabled,
            "typing": self.typing_enabled,
            "mode": current_mode
        }

        msg.data = json.dumps(data)

        self.publisher_.publish(msg)

        self.get_logger().info(
            f"Publishing: {msg.data}"
        )

    def update_settings(self):

        # Simulate changing privacy states
        self.camera_enabled = not self.camera_enabled

    # Optional future logic area


def main(args=None):

    rclpy.init(args=args)

    node = SettingsNode()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        node.get_logger().info(
            "Shutting down node..."
        )

    finally:
        node.destroy_node()
       
	if rclpy.ok():
		rclpy.shutdown()

if __name__ == '__main__':
    main()
