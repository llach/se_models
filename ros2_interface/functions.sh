source /opt/ros/${ROS_DISTRO}/setup.bash
echo "Sourced ROS 2 ${ROS_DISTRO}"

# Automatically link workspace packages from the mounted volume if they exist and are not already linked
if [ -d /home/ros/projects/se_models/ros2_interface/src ] && [ ! -L /home/ros/ws/src/se_models ]; then
  ln -sf /home/ros/projects/se_models/ros2_interface/src/se_models /home/ros/ws/src/se_models
  ln -sf /home/ros/projects/se_models/ros2_interface/src/se_models_msgs /home/ros/ws/src/se_models_msgs
fi

function s {
  # Source the overlay workspace, if built
  if [ -f /home/ros/ws/install/setup.bash ]
  then
    source /home/ros/ws/install/setup.bash
    echo "Sourced workspace"
  fi
}

function cb {
  prev_dir=$(pwd)

  cd /home/ros/ws
  colcon build --symlink-install
  s
  cd $prev_dir
}

alias rviz='ros2 run rviz2 rviz2'

s # source install space
# uncomment and specify your domain ID so others on the network can't see your nodes
#export ROS_DOMAIN_ID=24

open_grippers() {
  # Run both service calls in the background
  ros2 service call /right_roller_gripper stack_msgs/srv/RollerGripper "finger_pos: 2500" &
  pid_right=$!

  ros2 service call /left_roller_gripper stack_msgs/srv/RollerGripper "finger_pos: 2000" &
  pid_left=$!

  # Wait for both background jobs to finish
  wait $pid_right
  wait $pid_left

  echo "Both grippers finished."
}

activate_rollers() {
  # Default duration (if no argument is provided)
  duration=${1:-0.7}

  # Run both service calls in the background
  ros2 service call /right_roller_gripper stack_msgs/srv/RollerGripper "{roller_duration: ${duration}, roller_vel: -80}" &
  pid_right=$!

  ros2 service call /left_roller_gripper stack_msgs/srv/RollerGripper "{roller_duration: ${duration}, roller_vel: 80}" &
  pid_left=$!

  # Wait for both background jobs to finish
  wait $pid_right
  wait $pid_left

  echo "Both grippers finished (duration = ${duration})."
}



close_grippers() {
  # Run both service calls in the background
  ros2 service call /right_roller_gripper stack_msgs/srv/RollerGripper "finger_pos: 800" &
  pid_right=$!

  ros2 service call /left_roller_gripper stack_msgs/srv/RollerGripper "finger_pos: 3400" &
  pid_left=$!

  # Wait for both background jobs to finish
  wait $pid_right
  wait $pid_left

  echo "Both grippers finished."
}

partly_close_grippers() {
  camera_grip=${1:-1000}
  normal_grip=${2:-3200}

  # Run both service calls in the background
  ros2 service call /right_roller_gripper stack_msgs/srv/RollerGripper "finger_pos: ${camera_grip}" &
  pid_right=$!

  ros2 service call /left_roller_gripper stack_msgs/srv/RollerGripper "finger_pos: ${normal_grip}" &
  pid_left=$!

  # Wait for both background jobs to finish
  wait $pid_right
  wait $pid_left

  echo "Both grippers finished."
}
