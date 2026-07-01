"""
bridge_api.py — ROS2 → Flask bridge for the web dashboard.

Subscribes to /fatigue_status (String/JSON) and /alarm_triggered (Bool)
from the ROS2 nodes, and re-serves that data via the exact same HTTP
endpoints as the original backend/api_server.py.

Run separately from the ROS2 launch file (not a managed ROS2 node):
    source /opt/ros/jazzy/setup.bash
    source ~/ros2-fatigue-detection/install/setup.bash
    python3 bridge_api.py
"""
import json
import threading
import time
from collections import deque

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String
from flask import Flask, jsonify

HISTORY_LIMIT = 60

_lock = threading.Lock()
_latest_status = {
    'status': 'starting',
    'fatigue_label': None,
    'fatigue_probability': None,
    'features': {},
    'timestamp': None,
    'alarm_triggered': False,
}
_history = deque(maxlen=HISTORY_LIMIT)


class BridgeNode(Node):

    def __init__(self):
        super().__init__('bridge_api_node')

        self.status_sub = self.create_subscription(
            String,
            '/fatigue_status',
            self._status_callback,
            10
        )

        self.alarm_sub = self.create_subscription(
            Bool,
            '/alarm_triggered',
            self._alarm_callback,
            10
        )

        self.get_logger().info(
            'Bridge node listening on /fatigue_status + /alarm_triggered'
        )

    def _status_callback(self, msg):
        global _latest_status
        try:
            data = json.loads(msg.data)
            with _lock:
                _latest_status.update({
                    'status': data.get('fatigue_label', 'starting'),
                    'fatigue_label': data.get('fatigue_label'),
                    'fatigue_probability': data.get('fatigue_probability'),
                    'features': data.get('features', {}),
                    'timestamp': data.get('timestamp', time.time()),
                })
                _history.append({
                    'timestamp': _latest_status['timestamp'],
                    'probability': _latest_status['fatigue_probability'],
                    'label': _latest_status['fatigue_label'],
                })
        except Exception as e:
            self.get_logger().error(f'status_callback error: {e}')

    def _alarm_callback(self, msg):
        with _lock:
            _latest_status['alarm_triggered'] = msg.data


app = Flask(__name__)


@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'source': 'ros2'})


@app.route('/api/status', methods=['GET'])
def status():
    with _lock:
        return jsonify(_latest_status)


@app.route('/api/history', methods=['GET'])
def history():
    with _lock:
        return jsonify(list(_history))


def ros2_spin_thread():
    rclpy.init()
    node = BridgeNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    t = threading.Thread(target=ros2_spin_thread, daemon=True)
    t.start()

    print('[BRIDGE] API server starting on http://0.0.0.0:5000')
    print('[BRIDGE] Endpoints: /api/health  /api/status  /api/history')
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
