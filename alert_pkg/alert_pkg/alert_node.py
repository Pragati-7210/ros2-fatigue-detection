import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32


class AlertNode(Node):

    def __init__(self):

        super().__init__('alert_node')

        self.subscription = self.create_subscription(
            Float32,
            '/fatigue_score',
            self.alert_callback,
            10
        )

    def alert_callback(self, msg):

        fatigue_score = msg.data

        if fatigue_score < 1.0:

            status = 'NORMAL'

        elif fatigue_score < 2.0:

            status = 'MILD FATIGUE'

        else:

            status = 'SEVERE FATIGUE'

        self.get_logger().info(
            f'Fatigue Score: {fatigue_score:.2f} | Status: {status}'
        )


def main(args=None):

    rclpy.init(args=args)

    node = AlertNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()