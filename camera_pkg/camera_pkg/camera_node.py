import rclpy
from rclpy.node import Node

from std_msgs.msg import Float32

import cv2
import mediapipe as mp

from camera_pkg.ear_detector import EyeFatigueDetector
from camera_pkg.mar_detector import MouthFatigueDetector
from camera_pkg.head_detector import HeadPostureDetector


class CameraNode(Node):

    def __init__(self):

        super().__init__('camera_node')

        self.eye_pub = self.create_publisher(
            Float32,
            '/eye_data',
            10
        )

        self.yawn_pub = self.create_publisher(
            Float32,
            '/yawn_data',
            10
        )

        self.posture_pub = self.create_publisher(
            Float32,
            '/posture_data',
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

        self.timer = self.create_timer(
            0.03,
            self.process_frame
        )

    def process_frame(self):

        ret, frame = self.cap.read()

        if not ret:

            self.get_logger().warning(
                'Failed to capture frame'
            )

            return

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        result = self.face_mesh.process(rgb)

        landmarks = None

        if result.multi_face_landmarks:

            landmarks = (
                result
                .multi_face_landmarks[0]
                .landmark
            )

        self.eye_detector.process(
            landmarks,
            frame.shape
        )

        self.mouth_detector.process(
            landmarks,
            frame.shape
        )

        self.head_detector.process(
            landmarks,
            frame.shape
        )

        self.eye_detector.draw_overlay(frame)

        self.mouth_detector.draw_overlay(frame)

        self.head_detector.draw_overlay(frame)

        cv2.imshow(
            "ROS2 Fatigue Camera System",
            frame
        )

        cv2.waitKey(1)
        eye_msg = Float32()
        eye_msg.data = float(
            self.eye_detector.get_features().get(
                "avg_ear",
                0.0
            )
        )

        yawn_msg = Float32()
        yawn_msg.data = float(
            self.mouth_detector.get_features().get(
                "yawn_count",
                0.0
            )
        )

        posture_msg = Float32()
        posture_msg.data = float(
            self.head_detector.get_features().get(
                "nod_count",
                0.0
            )
        )

        self.eye_pub.publish(eye_msg)

        self.yawn_pub.publish(yawn_msg)

        self.posture_pub.publish(posture_msg)

        print(
            "PUBLISHED:",
            eye_msg.data,
            yawn_msg.data,
            posture_msg.data
        )


def main(args=None):

    rclpy.init(args=args)

    node = CameraNode()

    rclpy.spin(node)

    node.cap.release()

    cv2.destroyAllWindows()

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':

    main()
