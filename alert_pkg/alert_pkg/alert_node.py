"""
alert_node.py — ROS2 alert node for fatigue detection.

Replaces the simple <1.0/<2.0 threshold check with the validated rolling
window logic: alarm triggers when >=70% of the last 18 readings (3 minutes)
are FATIGUED, requiring a full 18-reading history before firing.
"""
from collections import deque

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, Float32

ALARM_THRESHOLD_MINUTES = 3.0
BUFFER_WINDOW_SECONDS = 10.0
ALARM_THRESHOLD_WINDOWS = int(
    ALARM_THRESHOLD_MINUTES * 60 / BUFFER_WINDOW_SECONDS
)
ALARM_RATIO = 0.70


class AlertNode(Node):

    def __init__(self):
        super().__init__('alert_node')

        self.subscription = self.create_subscription(
            Float32,
            '/fatigue_score',
            self.alert_callback,
            10
        )

        self.alarm_pub = self.create_publisher(Bool, '/alarm_triggered', 10)

        self._window = deque(maxlen=ALARM_THRESHOLD_WINDOWS)
        self._alarm_active = False

        self.get_logger().info(
            f'Alert node ready — alarm fires when >={ALARM_RATIO*100:.0f}% '
            f'of the last {ALARM_THRESHOLD_WINDOWS} windows '
            f'({ALARM_THRESHOLD_MINUTES} min) are FATIGUED'
        )

    def alert_callback(self, msg):
        fatigue_prob = msg.data

        is_fatigued = 1 if fatigue_prob >= 0.5 else 0
        self._window.append(is_fatigued)

        window_full = len(self._window) == ALARM_THRESHOLD_WINDOWS
        if window_full:
            ratio = sum(self._window) / ALARM_THRESHOLD_WINDOWS
            alarm = ratio >= ALARM_RATIO
        else:
            ratio = sum(self._window) / max(len(self._window), 1)
            alarm = False

        label = 'FATIGUED' if is_fatigued else 'ALERT'
        self.get_logger().info(
            f'Fatigue: {fatigue_prob*100:.1f}% | Status: {label} | '
            f'Ratio: {ratio*100:.0f}% ({sum(self._window)}'
            f'/{len(self._window)}) | '
            f'Alarm: {"ON" if alarm else "off"}'
        )

        alarm_msg = Bool()
        alarm_msg.data = alarm
        self.alarm_pub.publish(alarm_msg)

        if alarm and not self._alarm_active:
            self.get_logger().warn(
                f'ALARM TRIGGERED — sustained fatigue detected '
                f'({ratio*100:.0f}% of last {ALARM_THRESHOLD_WINDOWS} windows)'
            )
        elif not alarm and self._alarm_active:
            self.get_logger().info('Alarm cleared — user appears alert again.')

        self._alarm_active = alarm


def main(args=None):
    rclpy.init(args=args)
    node = AlertNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
