"""
fusion_node.py — ROS2 fusion node for fatigue detection.

Replaces the heuristic compute_fatigue() placeholder with the real trained
Random Forest model. Subscribes to /camera_features and /typing_features
(both JSON strings), merges them, builds the exact 19-feature vector the
model was trained on, and publishes the result.
"""
import json
import csv
import os
import time
from datetime import datetime
from collections import deque

import joblib
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, String

SYNC_TOLERANCE = 5.0


class FusionNode(Node):

    def __init__(self):
        super().__init__('fusion_node')

        _this_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(_this_dir, 'fatigue_model.pkl')
        meta_path = os.path.join(_this_dir, 'fatigue_model_meta.pkl')

        try:
            self._model = joblib.load(model_path)
            self._meta = joblib.load(meta_path)
            self._feature_order = self._meta['feature_order']
            self._clip_caps = self._meta['clip_caps']
            self._model_available = True
            self.get_logger().info('Fatigue model loaded successfully.')
        except Exception as e:
            self._model = None
            self._meta = None
            self._feature_order = []
            self._clip_caps = {}
            self._model_available = False
            self.get_logger().error(
                f'Could not load model: {e} — predictions disabled.'
            )

        self.camera_sub = self.create_subscription(
            String, '/camera_features', self.camera_callback, 10
        )
        self.typing_sub = self.create_subscription(
            String, '/typing_features', self.typing_callback, 10
        )
        self.permissions_sub = self.create_subscription(
            String, '/permissions', self.permissions_callback, 10
        )

        self.score_pub = self.create_publisher(Float32, '/fatigue_score', 10)
        self.status_pub = self.create_publisher(
            String, '/fatigue_status', 10
        )

        self._latest_camera = None
        self._latest_camera_ts = None
        self._latest_typing = None
        self._latest_typing_ts = None

        self.camera_enabled = True
        self.typing_enabled = True

        self.csv_file = os.path.expanduser('~/fatigue_dataset.csv')
        self._init_csv()

        self.get_logger().info('Fusion node ready.')

    def _init_csv(self):
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, mode='w', newline='') as f:
                csv.writer(f).writerow([
                    'timestamp', 'fatigue_label', 'fatigue_probability',
                    'camera_features', 'typing_features'
                ])

    def camera_callback(self, msg):
        try:
            self._latest_camera = json.loads(msg.data)
            self._latest_camera_ts = time.time()
            self._try_fuse()
        except Exception as e:
            self.get_logger().error(f'camera_callback error: {e}')

    def typing_callback(self, msg):
        try:
            self._latest_typing = json.loads(msg.data)
            self._latest_typing_ts = time.time()
            self._try_fuse()
        except Exception as e:
            self.get_logger().error(f'typing_callback error: {e}')

    def permissions_callback(self, msg):
        try:
            permissions = json.loads(msg.data)
            self.camera_enabled = permissions.get('camera', True)
            self.typing_enabled = permissions.get('typing', True)
            current_mode = permissions.get('mode', 'unknown')
            self.get_logger().info(
                f'Permissions Updated | Mode: {current_mode} | '
                f'Camera: {self.camera_enabled} | '
                f'Typing: {self.typing_enabled}'
            )
        except Exception as e:
            self.get_logger().error(f'permissions_callback error: {e}')

    def _try_fuse(self):
        if self._latest_camera is None or self._latest_typing is None:
            return

        now = time.time()
        camera_age = now - self._latest_camera_ts
        typing_age = now - self._latest_typing_ts

        if abs(camera_age - typing_age) > SYNC_TOLERANCE:
            return

        merged = {}
        if self.camera_enabled:
            merged.update(self._latest_camera)
        if self.typing_enabled:
            merged.update(self._latest_typing)

        try:
            vector = []
            for feat in self._feature_order:
                val = float(merged.get(feat, 0.0))
                if feat in self._clip_caps:
                    val = min(val, self._clip_caps[feat])
                vector.append(val)
        except Exception as e:
            self.get_logger().error(f'Feature vector build error: {e}')
            return

        if not self._model_available:
            self.get_logger().warning('Model not available — skipping.')
            return

        try:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                proba = self._model.predict_proba([vector])[0]

            fatigue_prob = float(proba[1])
            label = 'FATIGUED' if fatigue_prob >= 0.5 else 'ALERT'

            score_msg = Float32()
            score_msg.data = fatigue_prob
            self.score_pub.publish(score_msg)

            status = {
                'fatigue_probability': round(fatigue_prob, 4),
                'fatigue_label': label,
                'features': merged,
                'timestamp': time.time(),
            }
            status_msg = String()
            status_msg.data = json.dumps(status)
            self.status_pub.publish(status_msg)

            self.get_logger().info(
                f'Prediction: {label} ({fatigue_prob*100:.1f}%)'
            )

            ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(self.csv_file, mode='a', newline='') as f:
                csv.writer(f).writerow([
                    ts, label, round(fatigue_prob, 4),
                    json.dumps(self._latest_camera),
                    json.dumps(self._latest_typing)
                ])

        except Exception as e:
            self.get_logger().error(f'Prediction error: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = FusionNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
