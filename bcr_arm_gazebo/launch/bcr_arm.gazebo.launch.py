import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    bcr_arm_description_share = get_package_share_directory('bcr_arm_description')
    parent_dir = os.path.dirname(bcr_arm_description_share)
    
    current_gz_resource_path = os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    new_paths = [parent_dir]
    
    for path_to_add in new_paths:
        if path_to_add not in current_gz_resource_path.split(os.pathsep):
            current_gz_resource_path = path_to_add + os.pathsep + current_gz_resource_path
            
    if current_gz_resource_path.endswith(os.pathsep): 
        current_gz_resource_path = current_gz_resource_path[:-1]

    os.environ['GZ_SIM_RESOURCE_PATH'] = current_gz_resource_path
    # For debugging
    # print(f"GZ_SIM_RESOURCE_PATH: {os.environ['GZ_SIM_RESOURCE_PATH']}")

    # Declare launch arguments
    declared_arguments = []

    declared_arguments.append(
        DeclareLaunchArgument(
            'robot_name',
            default_value='bcr_arm',
            description='Name of the robot'
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'prefix',
            default_value='',
            description='Prefix for robot joints and links'
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'use_gazebo', 
            default_value='true',
            description='Whether to use Gazebo simulation'
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'add_world', default_value='true',
            choices=['true', 'false'],
            description='Whether to add world link to URDF'
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'base_link',
            default_value='base_link',
            description='Name of the base link'
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'base_type', 
            default_value='g_shape',
            description='Type of the base (passed to XACRO)'
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'flange_link', 
            default_value='link6_flange', 
            description='Name of the flange link (passed to XACRO)'
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'gripper_type', 
            default_value='adaptive_gripper',
            description='Type of the gripper (passed to XACRO)'
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'use_camera', 
            default_value='false', 
            choices=['true', 'false'],
            description='Whether to use camera in URDF (passed to XACRO)'
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'world_path',
            default_value=PathJoinSubstitution([
                FindPackageShare('bcr_arm_gazebo'), 'worlds', 'empty.world'
            ]),
            description='Path to the Gazebo world file'
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            'ros2_controllers_path',
            default_value=PathJoinSubstitution([
                FindPackageShare('bcr_arm_moveit_config'), 'config', 'ros2_controllers.yaml'
            ]),
            description='Path to the ros2_controllers.yaml file'
        )
    )

    robot_name_lc = LaunchConfiguration('robot_name')
    prefix_lc = LaunchConfiguration('prefix')
    use_gazebo_lc = LaunchConfiguration('use_gazebo')
    add_world_lc = LaunchConfiguration('add_world')
    base_link_lc = LaunchConfiguration('base_link')
    base_type_lc = LaunchConfiguration('base_type')
    flange_link_lc = LaunchConfiguration('flange_link')
    gripper_type_lc = LaunchConfiguration('gripper_type')
    use_camera_lc = LaunchConfiguration('use_camera')
    use_sim_time_lc = LaunchConfiguration('use_sim_time')
    world_path_lc = LaunchConfiguration('world_path')
    ros2_controllers_path_lc = LaunchConfiguration('ros2_controllers_path')

    # Get URDF via xacro - separate for spawning and robot_state_publisher
    robot_description_command = Command([
        PathJoinSubstitution([FindExecutable(name='xacro')]), ' ',
        PathJoinSubstitution([FindPackageShare('bcr_arm_description'), 'urdf', 'robots', 'bcr_arm.urdf.xacro']), ' ',
        'robot_name:=', robot_name_lc, ' ',
        'prefix:=', prefix_lc, ' ',
        'use_gazebo:=', use_gazebo_lc, ' ',
        'add_world:=', add_world_lc, ' ',
        'base_link:=', base_link_lc, ' ',
        'base_type:=', base_type_lc, ' ',
        'flange_link:=', flange_link_lc, ' ',
        'gripper_type:=', gripper_type_lc, ' ',
        'use_camera:=', use_camera_lc, ' ',
        'ros2_controllers_path:=', ros2_controllers_path_lc
    ])

    robot_description_content = ParameterValue(robot_description_command, value_type=str)
    robot_description_param = {'robot_description': robot_description_content}

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description_param, {'use_sim_time': use_sim_time_lc}]
    )

    gazebo_sim_node = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py'])
        ),
        launch_arguments={'gz_args': ['-r -v 4 ', world_path_lc]}.items()
    )

    spawn_entity_node = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=[
            '-string', robot_description_command,
            '-name', robot_name_lc,
            '-allow_renaming', 'true',
            # '-x', '0.0', '-y', '0.0', '-z', '0.1', # Optional: specify spawn pose
        ]
    )

    spawn_joint_state_broadcaster_node = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', ['/controller_manager']],
        output='screen',
    )

    spawn_joint_trajectory_controller_node = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_trajectory_controller', '--controller-manager', ['/controller_manager']],
        output='screen',
    )

    delay_jsb_after_spawn = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_entity_node,
            on_exit=[spawn_joint_state_broadcaster_node],
        )
    )

    delay_jtc_after_jsb = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_joint_state_broadcaster_node,
            on_exit=[spawn_joint_trajectory_controller_node],
        )
    )

    return LaunchDescription(declared_arguments + [
        robot_state_publisher_node,
        gazebo_sim_node,
        spawn_entity_node,
        delay_jsb_after_spawn,
        delay_jtc_after_jsb,
    ])
