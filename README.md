# BCR Arm


https://github.com/user-attachments/assets/8400757d-da8a-446a-a5b3-db223acf94b4


## About

This repository contains a Gazebo Fortress simulation for a 7-DOF robotic arm. It includes ROS2 Control integration and MoveIt for motion planning. Currently, the project supports:

1.  [ROS2 Humble + Gazebo Fortress (Ubuntu 22.04)](#humble--fortress-ubuntu-2204)
2. [ROS2 Jazzy + Gazebo Harmonic (Ubuntu 24.04)](#jazzy--harmonic-ubuntu-2404)
3.  [Nvidia Isaac Sim](#4-isaac-sim--moveit)


This branch contains the code and scripts for running on ROS2 Humble + Ignition Gazebo Fortress.

## Humble + Fortress (Ubuntu 22.04)

### Dependencies

Ensure you have ROS2 Humble and Gazebo Fortress installed.

```bash
# Install ROS2 Humble (if not already installed)
sudo apt update
sudo apt install -y ros-humble-desktop

# Install Gazebo Fortress
sudo apt install -y gz-fortress
```

Project-specific dependencies can be installed using `rosdep`:
```bash
# From the root directory of your workspace (e.g., ~/bcr_ws)
rosdep install --from-paths src --ignore-src -r -y
```

## Jazzy + Harmonic (Ubuntu 24.04)

### Dependencies

Ensure you have ROS2 Jazzy and Gazebo Harmonic installed.

```bash
# Install ROS2 jazzy (if not already installed)
sudo apt update
sudo apt install -y ros-jazzy-desktop

# Install Gazebo Harmonic
sudo apt install -y gz-harmonic
```

Project-specific dependencies can be installed using `rosdep`:
```bash
# From the root directory of your workspace (e.g., ~/bcr_ws)
rosdep install --from-paths src --ignore-src -r -y
```

### Building from Source

```bash
# From the root of your workspace
colcon build --symlink-install

# Source the workspace
source install/setup.bash
```

### Launch Files

#### 1. Gazebo Simulation with ROS2 Control and MoveIt2 Motion Planning
To launch the Gazebo simulation with ROS2 Control and MoveIt2 for motion planning, use the following command:
```bash
ros2 launch bcr_arm_gazebo bcr_arm.gazebo_moveit.launch.py
```
This starts:
*   Gazebo Fortress with the BCR Arm.
*   ROS2 controllers for the arm.
*   MoveIt2 for motion planning and visualization in RViz.

#### 2. Gazebo Simulation with ROS2 Control

This is the primary launch file to bring up the full simulation environment.
```bash
ros2 launch bcr_arm_gazebo bcr_arm.gazebo.launch.py
```
This starts:
-   Gazebo Fortress with the BCR Arm.
-   ROS2 *mock* controllers for the arm. Use scripts from `bcr_arm_gazebo` to send commands to the arm.
-   Launch argument: `world_path:=<path_to_world>`

#### 3. MoveIt Demo (Standalone Motion Planning)

To launch MoveIt and RViz for motion planning (typically used with a running simulation or real hardware):
```bash
ros2 launch bcr_arm_moveit_config demo.launch.py
```

#### 4. Isaac Sim + Moveit 

To launch Isaac Sim and use Moveit for motion planning and control.

To launch the robot in Isaac Sim:

- Open Isaac Sim and load the [bcr_arm usd](isaacsim/bcr_arm_scene.usd).
- Add in extra viewports for different camera views.
- Start the Simulation: Run the simulation directly within Isaac Sim.

To view and launch moveit:

```bash
ros2 launch bcr_arm_moveit_config isaac_demo.launch.py
```

### Controlling the Arm

Once the simulation with controllers is running (e.g., via `bcr_arm.gazebo.launch.py`), you can send commands.

**Using the CLI Script:**

A Python script is provided to send predefined or custom joint goals.
```bash
# Ensure your workspace is sourced
# ros2 run bcr_arm_gazebo test_arm_movement.py
ros2 run bcr_arm_gazebo control_arm_cli.py
```
Follow the on-screen prompts to select poses or enter custom joint angles.


## Images

![Gazebo BCR Arm simulation with Moveit2](images/gz_img1.png)

![Isaac Sim BCR Arm simulation with Moveit2](images/isaac_img2.png)

![Jazzy BCR Arm simulation](images/jazzy_img3.png)
