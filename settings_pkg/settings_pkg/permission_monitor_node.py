
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json


class PermissionMonitorNode(Node):

    def __init__(self):
        super().__init__('permission_monitor_node')

        self.subscription = self.create_subscription(
            String,
            '/settings',
            self.settings_callback,
            10
        )

        self.get_logger().info(
            '[SYSTEM] Permission monitor active'
        )

    def settings_callback(self, msg):

        self.get_logger().info(f"Received: {msg.data}")
         
        try:
            data = json.loads(msg.data)
        except json.JSONDecodeError:
            self.get_logger().error("Invalid JSON received")
            return

        camera = data["camera"]
        typing = data["typing"]
        mode = data["mode"]

        valid_modes = [
            "FULL_MONITORING",
            "PRIVACY_MODE",
            "MINIMAL_MODE"
        ]
   
        if mode not in valid_modes:
            self.get_logger().warn(f"Invalid mode received: {mode}")
            return

        score = self.calculate_threat_score(data, mode)
        decision = self.apply_policy(camera, typing, mode, score)

        self.get_logger().info(f"Threat Score: {score}")
        self.get_logger().info(f"Decision: {decision}")

    #fatigue logic (your original idea kept clean)
        if camera and typing:

            self.get_logger().info(
                '[SYSTEM] Full fatigue monitoring active'
            )

            self.get_logger().info(
                '[CONFIDENCE] Fatigue detection confidence: HIGH'
            )

        elif not camera and typing:

            self.get_logger().warning(
                '[PRIVACY MODE] Visual monitoring disabled'
            )

            self.get_logger().info(
                '[SYSTEM] Switching to typing-only analysis'
            )

            self.get_logger().warning(
                '[CONFIDENCE] Fatigue detection confidence: MEDIUM'
            )

        elif not camera and not typing:

            self.get_logger().error(
                '[SYSTEM] Limited fatigue detection mode'
            )

            self.get_logger().error(
                '[CONFIDENCE] Fatigue detection confidence: LOW'
            )
       
      #threat scoring
       
      def calculate_threat_score(self, data, mode):

         score = 0
         valid_modes = ["FULL_MONITORING", "PRIVACY_MODE", "MINIMAL_MODE"]

         if mode not in valid_modes:
             score += 50

         if mode == "PRIVACY_MODE" and data.get("camera") == "ON":
             score += 40

         if data.get("typing") not in [True, False]:
             score += 25

         if mode == "FULL_MONITORING":
             score += 10

         return min(score, 100)

#firewall logic

      def apply_policy(self, camera, typing, mode, score):
  
         if score >= 70:
           return "BLOCK 🚫"

         if score >= 40:
           return "RESTRICT ⚠️"

         if mode == "PRIVACY_MODE" and camera == "ON":
           return "CAMERA DISABLED 🔒"

         if mode == "MINIMAL_MODE":
           return "CORE ONLY MODE 🧊"
      return "ALLOW ✅"

   def main(args=None):

      rclpy.init(args=args)

      node = PermissionMonitorNode()

      rclpy.spin(node)

      node.destroy_node()

      rclpy.shutdown()


if __name__ == '__main__':
    main()

