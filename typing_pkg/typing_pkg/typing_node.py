"""
typing_node.py — ROS2 keyboard node for fatigue detection.

Replaces the original simple keystroke counter with the real
KeyboardTelemetryDetector, which computes the full 10-field feature dict
including deviation features from a personal baseline. Publishes on
/typing_features every 10 seconds, matching the camera node's window.
"""
import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from pynput import keyboard
from typing_pkg.keyboard_detector import KeyboardTelemetryDetector

BUFFER_WINDOW = 10.0  # seconds — must match camera_node and fusion_node


class TypingNode(Node):

    def __init__(self):
        super().__init__('typing_node')

        self.features_pub = self.create_publisher(
            String,
            '/typing_features',
            10
        )

        self.detector = KeyboardTelemetryDetector()

        self.listener = keyboard.Listener(
            on_press=self.detector.on_press
        )
        self.listener.start()

        self.window_timer = self.create_timer(
            BUFFER_WINDOW,
            self.publish_window
        )

        self.get_logger().info(
            'Typing node started — publishing /typing_features every '
            f'{BUFFER_WINDOW}s'
        )

    def publish_window(self):
        features = self.detector.process(BUFFER_WINDOW)

        msg = String()
        msg.data = json.dumps(features)
        self.features_pub.publish(msg)

        self.get_logger().info(
            f'Published /typing_features: '
            f'typing_speed={features.get("typing_speed", 0):.3f} '
            f'speed_deviation={features.get("speed_deviation", 0):.3f}'
        )


def main(args=None):
    rclpy.init(args=args)
    node = TypingNode()
    try:
        rclpy.spin(node)
    finally:
        node.listener.stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
