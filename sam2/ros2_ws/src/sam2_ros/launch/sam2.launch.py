from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'api_url',
            default_value='http://localhost:8001/predict_sam2',
            description='URL of the SAM2 FastAPI server'
        ),
        Node(
            package='sam2_ros',
            executable='sam2_node',
            name='sam2_node',
            parameters=[
                {'api_url': LaunchConfiguration('api_url')}
            ]
        )
    ])
