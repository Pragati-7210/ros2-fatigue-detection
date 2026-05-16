from launch import LaunchDescription

from launch_ros.actions import Node


def generate_launch_description():

    return LaunchDescription([

        Node(
            package='settings_pkg',
            executable='settings_node',
            output='screen'
        ),

        Node(
            package='fusion_pkg',
            executable='fusion_node',
            output='screen'
        ),

        Node(
            package='alert_pkg',
            executable='alert_node',
            output='screen'
        ),

	 Node(
            package='camera_pkg',
            executable='camera_node',
            output='screen'
        ),

    ])
