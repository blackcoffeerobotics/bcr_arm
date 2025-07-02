#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import (
    AppendEnvironmentVariable,
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    TimerAction
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    """
    Generate a launch description for the BCR ARM Gazebo simulation with RViz.

    This function sets up all necessary parameters, paths, and nodes required to launch
    the Gazebo simulation with the BCR ARM robot and RViz for visualization.
    """
    package_name_gazebo = 'bcr_arm_gazebo'
    package_name_description = 'bcr_arm_description'
    package_name_moveit = 'bcr_arm_moveit_config'

    default_robot_name = 'bcr_arm'
    gazebo_models_path_name = 'models'  # Relative path within bcr_arm_gazebo
    gazebo_worlds_path_name = 'worlds'  # Relative path within bcr_arm_gazebo
    default_world_file = 'pick_and_place_demo.world'
    default_rviz_config_file = 'bcr_arm.rviz'
    urdf_filename = 'bcr_arm.urdf.xacro'

    # Get package share directories
    pkg_ros_gz_sim = FindPackageShare(package='ros_gz_sim').find('ros_gz_sim')
    pkg_share_gazebo = FindPackageShare(package=package_name_gazebo).find(package_name_gazebo)
    pkg_share_description = FindPackageShare(
        package=package_name_description).find(package_name_description)
    pkg_share_moveit = FindPackageShare(package=package_name_moveit).find(package_name_moveit)

    default_urdf_model_path = PathJoinSubstitution([
        pkg_share_description, 'urdf', 'robots', urdf_filename])

    load_controllers = LaunchConfiguration('load_controllers')
    robot_name = LaunchConfiguration('robot_name')
    use_rviz = LaunchConfiguration('use_rviz')
    use_camera = LaunchConfiguration('use_camera')
    use_gazebo = LaunchConfiguration('use_gazebo')
    use_robot_state_pub = LaunchConfiguration('use_robot_state_pub')
    use_sim_time = LaunchConfiguration('use_sim_time')
    world_file = LaunchConfiguration('world_file')
    rviz_config_file = LaunchConfiguration('rviz_config_file')

    # Pose configuration variables
    x = LaunchConfiguration('x')
    y = LaunchConfiguration('y')
    z = LaunchConfiguration('z')
    roll = LaunchConfiguration('roll')
    pitch = LaunchConfiguration('pitch')
    yaw = LaunchConfiguration('yaw')

    # Path to the world file
    world_path = PathJoinSubstitution([
        pkg_share_gazebo,
        gazebo_worlds_path_name,
        world_file
    ])

    rviz_config_file_path = PathJoinSubstitution([
        pkg_share_description, 'rviz', rviz_config_file
    ])

    declare_robot_name_cmd = DeclareLaunchArgument(
        name='robot_name',
        default_value=default_robot_name,
        description='The name for the BCR ARM robot')

    declare_load_controllers_cmd = DeclareLaunchArgument(
        name='load_controllers',
        default_value='true',
        description='Flag to enable loading of ROS 2 controllers')

    declare_use_robot_state_pub_cmd = DeclareLaunchArgument(
        name='use_robot_state_pub',
        default_value='true',
        description='Flag to enable robot state publisher')

    declare_use_camera_cmd = DeclareLaunchArgument(
        name='use_camera',
        default_value='true', # Default to true as depth camera is relevant
        description='Flag to enable the RGBD camera and image bridge')

    declare_use_gazebo_cmd = DeclareLaunchArgument(
        name='use_gazebo',
        default_value='true',
        description='Flag to enable Gazebo')

    declare_use_rviz_cmd = DeclareLaunchArgument(
        name='use_rviz',
        default_value='true',
        description='Flag to enable RViz')

    declare_rviz_config_file_cmd = DeclareLaunchArgument(
        name='rviz_config_file',
        default_value=default_rviz_config_file,
        description='RViz configuration file name (e.g., bcr_arm.rviz)')

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        name='use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true')

    declare_world_cmd = DeclareLaunchArgument(
        name='world_file',
        default_value=default_world_file,
        description='World file name (e.g., empty.world, pick_and_place_demo.world)')

    # Pose arguments
    declare_x_cmd = DeclareLaunchArgument(name='x', default_value='0.0', description='x component of initial position')
    declare_y_cmd = DeclareLaunchArgument(name='y', default_value='0.0', description='y component of initial position')
    declare_z_cmd = DeclareLaunchArgument(name='z', default_value='0.00', description='z component of initial position')
    declare_roll_cmd = DeclareLaunchArgument(name='roll', default_value='0.0', description='roll angle of initial orientation')
    declare_pitch_cmd = DeclareLaunchArgument(name='pitch', default_value='0.0', description='pitch angle of initial orientation')
    declare_yaw_cmd = DeclareLaunchArgument(name='yaw', default_value='0.0', description='yaw angle of initial orientation')

    bcr_arm_gazebo_models_dir = os.path.join(pkg_share_gazebo, gazebo_models_path_name)
    bcr_arm_description_share_dir_parent = os.path.abspath(os.path.join(pkg_share_description, '..'))

    set_gz_resource_path_for_gazebo_pkg = AppendEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH',
        bcr_arm_gazebo_models_dir
    )
    set_gz_resource_path_for_description_pkg = AppendEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH',
        bcr_arm_description_share_dir_parent
    )

    # Robot State Publisher
    robot_state_publisher_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(pkg_share_description, 'launch', 'bcr_arm_description.launch.py')
        ]),
        launch_arguments={
            'robot_name': robot_name,
            'use_camera': use_camera,
            'use_gazebo': use_gazebo, # URDF needs to know if it's for Gazebo (e.g. for plugins)
            'use_sim_time': use_sim_time,
            'launch_rviz': 'false'  # Prevent bcr_arm_description.launch.py from starting its own RViz
        }.items(),
        condition=IfCondition(use_robot_state_pub)
    )

    start_controller_manager_cmd = Node(
        package='controller_manager',
        executable='ros2_control_node',
        name='controller_manager', # Default name, can be customized
        output='screen',
        parameters=[
            default_urdf_model_path, # Path to the URDF file
            os.path.join(pkg_share_moveit, 'config', 'bcr_arm', 'ros2_controllers.yaml')
        ],
        condition=IfCondition(load_controllers) # Only run if load_controllers is true
    )

    load_controllers_cmd = TimerAction(
        period=20.0,  # Wait for Gazebo and controller_manager to initialize
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    os.path.join(pkg_share_moveit, 'launch', 'spawn_controllers.launch.py')
                ]),
                launch_arguments={
                    'use_sim_time': use_sim_time
                }.items()
            )
        ],
        condition=IfCondition(load_controllers)
    )

    start_gazebo_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')),
        launch_arguments=[('gz_args', [' -r -v 4 ', world_path])],
        condition=IfCondition(use_gazebo)
    )

    start_gazebo_ros_bridge_cmd = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            # Bridge joint states from Gazebo to ROS
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
            # Bridge TF from Gazebo to ROS
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
        ],
        output='screen',
        condition=IfCondition(use_gazebo)
    )

    # ROS-Gazebo Image Bridge for depth camera
    start_gazebo_ros_image_bridge_cmd = Node(
        package='ros_gz_image',
        executable='image_bridge',
        arguments=[
            # Bridge the actual camera topics from Gazebo
            '/camera/image_raw',
            '/camera/depth/image_raw',
            '/camera/camera_info',
            '/camera/depth/camera_info',
        ],
        remappings=[
            ('/camera/image_raw', '/camera/color/image_raw'),
            ('/camera/camera_info', '/camera/color/camera_info'),
        ],
        output='screen',
        condition=IfCondition(use_camera)
    )

    # ROS-Gazebo Point Cloud Bridge for depth camera
    start_gazebo_ros_pointcloud_bridge_cmd = Node(
        package='ros_gz_point_cloud',
        executable='point_cloud_bridge',
        arguments=['/camera/points'],
        remappings=[
            ('/camera/points', '/camera/depth/points'),
        ],
        output='screen',
        condition=IfCondition(use_camera)
    )

    # Spawn the robot in Gazebo
    start_gazebo_ros_spawner_cmd = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=[
            '-topic', '/robot_description', # Topic where URDF is published
            '-name', robot_name,
            '-allow_renaming', 'true',
            '-x', x,
            '-y', y,
            '-z', z,
            '-R', roll,
            '-P', pitch,
            '-Y', yaw
        ],
        condition=IfCondition(use_gazebo)
    )

    # Start RViz
    start_rviz_cmd = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file_path],
        condition=IfCondition(use_rviz),
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # Create the launch description and populate
    ld = LaunchDescription()

    # Declare launch options
    ld.add_action(declare_robot_name_cmd)
    ld.add_action(declare_load_controllers_cmd)
    ld.add_action(declare_use_camera_cmd)
    ld.add_action(declare_use_gazebo_cmd)
    ld.add_action(declare_use_rviz_cmd)
    ld.add_action(declare_rviz_config_file_cmd)
    ld.add_action(declare_use_robot_state_pub_cmd)
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_world_cmd)

    # Add pose arguments
    ld.add_action(declare_x_cmd)
    ld.add_action(declare_y_cmd)
    ld.add_action(declare_z_cmd)
    ld.add_action(declare_roll_cmd)
    ld.add_action(declare_pitch_cmd)
    ld.add_action(declare_yaw_cmd)

    # Add actions to execute
    # Set environment variables first
    ld.add_action(set_gz_resource_path_for_gazebo_pkg)
    ld.add_action(set_gz_resource_path_for_description_pkg)

    # Start simulation components
    ld.add_action(robot_state_publisher_cmd) # Publishes /robot_description and TF
    ld.add_action(start_controller_manager_cmd) # Starts ros2_control_node
    ld.add_action(load_controllers_cmd)      # Spawns controllers (JSA, JTC) after a delay
    ld.add_action(start_gazebo_cmd)          # Starts Gazebo server and GUI
    ld.add_action(start_gazebo_ros_bridge_cmd) # Bridges clock, joint_states, tf
    ld.add_action(start_gazebo_ros_image_bridge_cmd) # Bridges camera topics
    ld.add_action(start_gazebo_ros_spawner_cmd) # Spawns robot in Gazebo

    # Start visualization
    ld.add_action(start_rviz_cmd)

    return ld

