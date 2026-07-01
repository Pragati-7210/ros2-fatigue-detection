"""
camera_node.py — ROS2 camera node for fatigue detection.

Replaces the original per-frame publisher with a proper 10-second window
approach matching the trained model's expected input. Every 10 seconds,
publishes the full 9-field camera feature dict as JSON on /camera_features.
"""
import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import cv2
import mediapipe as mp
from camera_pkg.ear_detector import EyeFatigueDetector
from camera_pkg.mar_detector import MouthFatigueDetector
from camera_pkg.head_detector import HeadPostureDetector

BUFFER_WINDOW = 10.0  # seconds — must match fusion_node and typing_node


class CameraNode(Node):

    def __init__(self):
        super().__init__('camera_node')

        self.features_pub = self.create_publisher(
            String,
            '/camera_features',
            10
        )

        self.cap = cv2.VideoCapture(0)
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True
        )

        self.eye_detector = EyeFatigueDetector()
        self.mouth_detector = MouthFatigueDetector()
        self.head_detector = HeadPostureDetector()

        self.frame_timer = self.create_timer(0.03, self.process_frame)
        self.window_timer = self.create_timer(
            BUFFER_WINDOW,
            self.publish_window
        )

        self.get_logger().info(
            'Camera node started — publishing /camera_features every '
            f'{BUFFER_WINDOW}s'
        )

    def process_frame(self):
        try:
            ret, frame = self.cap.read()
        except cv2.error:
            ret, frame = False, None

        if not ret or frame is None:
            self.get_logger().warning('Failed to capture frame')
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.face_mesh.process(rgb)

        landmarks = None
        if result.multi_face_landmarks:
            landmarks = result.multi_face_landmarks[0].landmark

        self.eye_detector.process(landmarks, frame.shape)
        self.mouth_detector.process(landmarks, frame.shape)
        self.head_detector.process(landmarks, frame.shape)

        self.eye_detector.draw_overlay(frame)
        self.mouth_detector.draw_overlay(frame)
        self.head_detector.draw_overlay(frame)

        cv2.imshow('ROS2 Fatigue Camera System', frame)
        cv2.waitKey(1)

    def publish_window(self):
        eye_f = self.eye_detector.get_features()
        mouth_f = self.mouth_detector.get_features()
        head_f = self.head_detector.get_features()

        if not eye_f or not mouth_f or not head_f:
            self.get_logger().warning(
                'No face detected in this window — skipping publish'
            )
            self.eye_detector.reset_buffer()
            self.mouth_detector.reset_buffer()
            self.head_detector.reset_buffer()
            return

        features = {}
        features.update(eye_f)
        features.update(mouth_f)
        features.update(head_f)

        msg = String()
        msg.data = json.dumps(features)
        self.features_pub.publish(msg)

        self.get_logger().info(
            f'Published /camera_features: '
            f'avg_ear={features.get("avg_ear", 0):.3f} '
            f'yawn_count={features.get("yawn_count", 0)}'
        )

        self.eye_detector.reset_buffer()
        self.mouth_detector.reset_buffer()
        self.head_detector.reset_buffer()


def main(args=None):
    rclpy.init(args=args)
    node = CameraNode()
    try:
        rclpy.spin(node)
    finally:
        node.cap.release()
        cv2.destroyAllWindows()
        node.face_mesh.close()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
