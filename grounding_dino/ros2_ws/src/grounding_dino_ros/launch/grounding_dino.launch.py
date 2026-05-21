from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            'api_url',
            default_value='http://localhost:8000/predict_grounding_dino',
            description='URL of the GroundingDINO FastAPI server'
        ),
        Node(
            package='grounding_dino_ros',
            executable='grounding_dino_node',
            name='grounding_dino_node',
            parameters=[
                {'api_url': LaunchConfiguration('api_url')}
            ]
        )
    ])
