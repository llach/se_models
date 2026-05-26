from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'se_models'

setup(
    name=package_name,
    version='0.0.0',
    packages=['se_models_ros'],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
    ],
    install_requires=['setuptools', 'requests'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@todo.todo',
    description='ROS2 nodes for GroundingDINO and SAM2',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'grounding_dino_node = se_models_ros.grounding_dino_node:main',
            'sam2_node = se_models_ros.sam2_node:main'
        ],
    },
)
