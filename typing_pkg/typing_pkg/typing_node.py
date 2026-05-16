import rclpy
from pynput import keyboard
from rclpy.node import Node
from std_msgs.msg import Float32


class TypingNode(Node):

    def __init__(self):
        super().__init__('typing_node')

        self.key_count = 0

        self.listener = keyboard.Listener(
            on_press=self.on_key_press
        )

        self.listener.start()

        self.publisher_ = self.create_publisher(
            Float32,
            '/typing_data',
            10
        )

        timer_period = 1.0

        self.timer = self.create_timer(
            timer_period,
            self.publish_data
        )

    def on_key_press(self, key):
        self.key_count += 1

    def publish_data(self):

        msg = Float32()

        typing_speed = float(self.key_count)

        msg.data = typing_speed

        self.publisher_.publish(msg)

        self.key_count = 0

        self.get_logger().info(
            f'Publishing typing speed: {msg.data:.2f}'
        )


def main(args=None):

    rclpy.init(args=args)

    node = TypingNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()