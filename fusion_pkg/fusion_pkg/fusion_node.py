import json
import csv
import os
from datetime import datetime
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, String

class FusionNode(Node):

    def __init__(self):
        super().__init__('fusion_node')

        # Subscribers
        self.eye_sub = self.create_subscription(
            Float32,
            '/eye_data',
            self.eye_callback,
            10
        )

        self.typing_sub = self.create_subscription(
            Float32,
            '/typing_data',
            self.typing_callback,
            10
        )

        self.yawn_sub = self.create_subscription(
        Float32,
        '/yawn_data',
        self.yawn_callback,
        10
        )

        self.posture_sub = self.create_subscription(
            Float32,
            '/posture_data',
            self.posture_callback,
            10
        )

        self.permissions_sub = self.create_subscription(
        String,
        '/permissions',
        self.permissions_callback,
        10
    )

        # Publisher
        self.publisher_ = self.create_publisher(Float32, '/fatigue_score', 10)

        # Store latest values
        self.eye_value = 0.0
        self.camera_enabled = True
        self.typing_enabled = True
        self.typing_value = 0.0
        self.yawn_value = 0.0
        self.posture_value = 0.0
        self.csv_file = os.path.expanduser(
            '~/fatigue_dataset.csv'
        )

        self.initialize_csv()
        self.last_log_time = datetime.now()

    def initialize_csv(self):

        if not os.path.exists(self.csv_file):

            with open(
                self.csv_file,
                mode='w',
                newline=''
            ) as file:

                writer = csv.writer(file)

                writer.writerow([
                    'timestamp',
                    'eye',
                    'yawn',
                    'posture',
                    'typing',
                    'fatigue_score'
                ])

    def eye_callback(self, msg):
        self.eye_value = msg.data
        self.compute_fatigue()

    def typing_callback(self, msg):
        self.typing_value = msg.data
        self.compute_fatigue()

    def yawn_callback(self, msg):
        self.yawn_value = msg.data
        self.compute_fatigue()

    def posture_callback(self, msg):
        self.posture_value = msg.data
        self.compute_fatigue()

    def permissions_callback(self, msg):

        permissions = json.loads(msg.data)

        self.camera_enabled = permissions["camera"]

        self.typing_enabled = permissions["typing"]

        current_mode = permissions["mode"]

        self.get_logger().info(
            f'Permissions Updated | '
            f'Mode: {current_mode} | '
            f'Camera: {self.camera_enabled} | '
            f'Typing: {self.typing_enabled}'
        )

    
    def compute_fatigue(self):
        # Simple logic (placeholder)
        fatigue = 0.0

        if self.camera_enabled:

            fatigue += (
                (1.5 * self.eye_value)
                +
                (1.2 * self.yawn_value)
                +
                (1.0 * self.posture_value)
            )

        if self.typing_enabled:

            fatigue += (
                max(0.0, 2.0 - self.typing_value)
            )
            
        msg = Float32()
        msg.data = fatigue
        timestamp = datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S'
        )

        current_time = datetime.now()

        elapsed = (
            current_time
            - self.last_log_time
        ).total_seconds()

        if elapsed >= 1.0:

            with open(
                self.csv_file,
                mode='a',
                newline=''
            ) as file:

                writer = csv.writer(file)

                writer.writerow([
                    timestamp,
                    self.eye_value,
                    self.yawn_value,
                    self.posture_value,
                    self.typing_value,
                    fatigue
                ])

            self.last_log_time = current_time
        self.publisher_.publish(msg)

        self.get_logger().info(
            f'Fatigue: {fatigue:.2f} | '
            f'Eye: {self.eye_value:.2f} | '
            f'Yawn: {self.yawn_value:.2f} | '
            f'Posture: {self.posture_value:.2f} | '
            f'Typing: {self.typing_value:.2f}'
)

def main(args=None):
    rclpy.init(args=args)
    node = FusionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
