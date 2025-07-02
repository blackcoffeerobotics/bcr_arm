#!/usr/bin/env python3

# Still under development, this launch file sets up the BCR arm with MoveIt! and Gazebo simulation.
# there are some issues with moveit and using gazebo's physics engine for exceuting the planned trajectory

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from moveit_configs_utils import MoveItConfigsBuilder
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument(
            "use_sim_time",
            default_value="true",
            description="Use simulation (Gazebo) clock if true",
        )
    )

    use_sim_time = LaunchConfiguration("use_sim_time")

    bcr_arm_gazebo_pkg = FindPackageShare("bcr_arm_gazebo")
    
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([bcr_arm_gazebo_pkg, "launch", "bcr_arm.gazebo.launch.py"])
        ),
        launch_arguments={"use_sim_time": use_sim_time}.items(),
    )

    moveit_config = (
        MoveItConfigsBuilder("bcr_arm", package_name="bcr_arm_moveit_config")
        .robot_description(
            os.path.join(
                get_package_share_directory("bcr_arm_moveit_config"),
                "config",
                "bcr_arm.urdf.xacro",
            )
        )
        .robot_description_semantic(
            os.path.join(
                get_package_share_directory("bcr_arm_moveit_config"),
                "config",
                "bcr_arm.srdf",
            )
        )
        .trajectory_execution(
            os.path.join(
                get_package_share_directory("bcr_arm_moveit_config"),
                "config",
                "moveit_controllers.yaml",
            )
        )
        .to_moveit_configs()
    )

    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[moveit_config.to_dict(), {"use_sim_time": use_sim_time}],
        arguments=["--ros-args", "--log-level", "info"],
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", os.path.join(get_package_share_directory("bcr_arm_moveit_config"), "config", "moveit.rviz")],
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            {"use_sim_time": use_sim_time},
        ],
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
        output="screen",
    )

    joint_trajectory_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_trajectory_controller", "--controller-manager", "/controller_manager"],
        output="screen",
    )

    return LaunchDescription(
        declared_arguments + [
            gazebo_launch,
            move_group_node,
            rviz_node,
            # controller gets loaded by default by moveit_config
            # joint_state_broadcaster_spawner,
            # joint_trajectory_controller_spawner,
        ]
    )
