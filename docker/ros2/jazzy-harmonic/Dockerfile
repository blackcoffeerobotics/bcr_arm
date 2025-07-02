# ROS2 jazzy Base
FROM ros:jazzy

# Prevent hash mismatch error for apt-get update
RUN apt-get clean && rm -rf /var/lib/apt/lists/* && apt-get update -y

# Set environment variables for gpu support with nvidia - http://wiki.ros.org/docker/Tutorials/Hardware%20Acceleration#nvidia-docker2
ENV NVIDIA_VISIBLE_DEVICES \
    ${NVIDIA_VISIBLE_DEVICES:-all}
ENV NVIDIA_DRIVER_CAPABILITIES \
    ${NVIDIA_DRIVER_CAPABILITIES:+$NVIDIA_DRIVER_CAPABILITIES,}graphics

# Non Python/ROS Dependencies
RUN apt-get install --no-install-recommends -y \
    vim \
    software-properties-common

# Added updated mesa drivers for integration with cpu - https://github.com/ros2/rviz/issues/948#issuecomment-1428979499
# Ensure this PPA supports the Ubuntu version for ROS Jazzy (Ubuntu 24.04 Noble)
RUN add-apt-repository ppa:kisak/kisak-mesa && \
    apt-get update && apt-get upgrade -y

# Python Dependencies
# RUN apt-get install --no-install-recommends -y \
#     python3-pip

# ROS Dependencies
# For ROS Jazzy, ros-$ROS_DISTRO-ros-gz will install Gazebo Harmonic and related packages
RUN apt-get install --no-install-recommends -y \
    ros-$ROS_DISTRO-cyclonedds \
    ros-$ROS_DISTRO-rmw-cyclonedds-cpp \
    ros-$ROS_DISTRO-rviz2 \
    ros-$ROS_DISTRO-ros-gz \
    ros-$ROS_DISTRO-urdf-tutorial \
    ros-$ROS_DISTRO-controller-manager \
    ros-$ROS_DISTRO-ros2-control \
    ros-$ROS_DISTRO-ros2-controllers \
    ros-$ROS_DISTRO-gazebo-ros-pkgs \
    ros-$ROS_DISTRO-moveit \
    ros-$ROS_DISTRO-joint-state-publisher \
    ros-$ROS_DISTRO-joint-state-publisher-gui \
    ros-$ROS_DISTRO-robot-state-publisher \
    ros-$ROS_DISTRO-xacro \
    ros-$ROS_DISTRO-gripper-controllers \
    ros-$ROS_DISTRO-gz-ros2-control

# Use cyclone DDS by default
ENV RMW_IMPLEMENTATION rmw_cyclonedds_cpp

RUN echo "source /opt/ros/$ROS_DISTRO/setup.bash" >> /root/.bashrc
