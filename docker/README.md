# BCR ARM - Docker Usage

This document provides instructions for using Docker with the BCR Arm.

## Quick Start

### Build and Run Container

```bash
./docker/scripts/build_and_run.sh
```

Run from project root directory.

This script will:
- Build the Docker image with all necessary dependencies
- Start the container with GUI support
- Mount necessary directories for X11 forwarding

### Container Management Scripts

#### Start Container
```bash
./start_container.sh
```

#### Stop Container
```bash
./stop_container.sh
```

#### Open Bash Session in Running Container
```bash
./bash_into_container.sh
```

## Usage Inside Container

Once inside the container, you can run:

### Basic Gazebo Simulation
```bash
ros2 launch bcr_arm_gazebo bcr_arm.gazebo.launch.py
```

### MoveIt2 Demo (with fake hardware)
```bash
ros2 launch bcr_arm_moveit_config demo.launch.py
```

### Moveit2 Motion Planning with Gazebo
```bash
ros2 launch bcr_arm_gazebo bcr_arm.gazebo_moveit.launch.py
```

### Test Arm Movement
```bash
ros2 run bcr_arm_gazebo test_arm_movement.py
```

### Control Arm CLI
```bash
ros2 run bcr_arm_gazebo control_arm_cli.py
```
