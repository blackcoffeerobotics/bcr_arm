#!/usr/bin/env python3
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_share_description = get_package_share_directory('bcr_arm_description')
    default_urdf_path = PathJoinSubstitution([pkg_share_description, 'urdf', 'robots', 'bcr_arm.urdf.xacro'])
    default_rviz_config_path = PathJoinSubstitution([pkg_share_description, 'rviz', 'bcr_arm.rviz'])

    declared_arguments = [
        DeclareLaunchArgument(
            name='urdf_path',
            default_value=default_urdf_path,
            description='Absolute path to robot urdf file'
        ),
        DeclareLaunchArgument(
            name='rviz_config',
            default_value=default_rviz_config_path,
            description='Full path to the RVIZ config file to use'
        ),
        DeclareLaunchArgument(
            name='jsp_gui',
            default_value='true',
            choices=['true', 'false'],
            description='Flag to enable joint_state_publisher_gui'
        ),
        DeclareLaunchArgument(
            name='use_sim_time',
            default_value='false',
            description='Use simulation (Gazebo) clock if true (should be false for RViz only)'
        ),
        DeclareLaunchArgument( 
            name='launch_rviz',
            default_value='true',
            choices=['true', 'false'],
            description='Flag to enable RViz'
        ),
    ]

    urdf_path = LaunchConfiguration('urdf_path')
    rviz_config = LaunchConfiguration('rviz_config')
    jsp_gui = LaunchConfiguration('jsp_gui')
    use_sim_time = LaunchConfiguration('use_sim_time')
    launch_rviz = LaunchConfiguration('launch_rviz') 

    robot_description_command = Command([
        PathJoinSubstitution([FindExecutable(name='xacro')]), ' ',
        urdf_path, ' ',
        'use_gazebo:=false', ' ' 
    ])
    
    robot_description_param = {
        'robot_description': ParameterValue(robot_description_command, value_type=str)
    }

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[robot_description_param, {'use_sim_time': use_sim_time}]
    )

    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        condition=IfCondition(jsp_gui)
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(launch_rviz)
    )

    return LaunchDescription(declared_arguments + [
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz_node,
    ])