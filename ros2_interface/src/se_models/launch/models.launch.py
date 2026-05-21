import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    # Read ports from environment or use default ports
    # Port mappings: internal 8080 exposed to host ports
    grounding_dino_port = os.getenv('GROUNDING_DINO_PORT', '8000')
    sam2_port = os.getenv('SAM2_PORT', '8001')

    return LaunchDescription([
        DeclareLaunchArgument(
            'grounding_dino_url',
            default_value=f'http://localhost:{grounding_dino_port}',
            description='Base URL of the GroundingDINO FastAPI server'
        ),
        DeclareLaunchArgument(
            'sam2_url',
            default_value=f'http://localhost:{sam2_port}',
            description='Base URL of the SAM2 FastAPI server'
        ),
        Node(
            package='se_models',
            executable='grounding_dino_node',
            name='grounding_dino_node',
            parameters=[
                {'api_url': LaunchConfiguration('grounding_dino_url')}
            ]
        ),
        Node(
            package='se_models',
            executable='sam2_node',
            name='sam2_node',
            parameters=[
                {'api_url': LaunchConfiguration('sam2_url')}
            ]
        )
    ])
