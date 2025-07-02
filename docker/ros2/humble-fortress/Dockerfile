# ROS2 humble Base
FROM ros:humble

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

# Python Dependencies
RUN apt-get install --no-install-recommends -y \
    python3-pip \
    python3-rosdep

# Initialize rosdep (only if not already initialized)
RUN if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then \
        rosdep init; \
    fi && \
    rosdep update

# ROS Dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
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
    ros-$ROS_DISTRO-gripper-controllers \
    ros-$ROS_DISTRO-gz-ros2-control \
    ros-$ROS_DISTRO-warehouse-ros \
    ros-$ROS_DISTRO-ros2-controllers

# Install additional useful ROS packages
RUN apt-get install --no-install-recommends -y \
    ros-$ROS_DISTRO-cyclonedds \
    ros-$ROS_DISTRO-rmw-cyclonedds-cpp \
    ros-$ROS_DISTRO-rviz2 \
    ros-$ROS_DISTRO-ros-gz \
    ros-$ROS_DISTRO-gazebo-ros-pkgs \
    ros-$ROS_DISTRO-moveit \
    ros-$ROS_DISTRO-joint-state-publisher-gui

# Use cyclone DDS by default
ENV RMW_IMPLEMENTATION rmw_cyclonedds_cpp


# Install OpenGL and X11 libraries for GUI and GPU-agnostic support
RUN apt-get update && apt-get install --no-install-recommends -y \
    mesa-utils \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    x11-apps

# Copy workspace for dependency resolution
# Copy the bcr_arm folder to bcr_ws/src inside the container
RUN mkdir -p /bcr_ws/src
# Keep working directory at workspace root
WORKDIR /bcr_ws

RUN echo "source /opt/ros/$ROS_DISTRO/setup.bash" >> /root/.bashrc
RUN echo "source /bcr_ws/install/setup.bash" >> /root/.bashrc