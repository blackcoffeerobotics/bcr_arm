#!/bin/bash

# Build and run the BCR ARM container with proper GUI support

cd "$(dirname "$0")/../../"

docker build -t bcr_arm:humble-fortress -f docker/ros2/humble-fortress/Dockerfile .

# Checking if image was built successfully
if [ $? -ne 0 ]; then
    echo "Docker build failed!"
    exit 1
fi

xhost +local:docker

docker run -it -d --privileged --net=host \
    --name bcr_arm_container \
    --env="DISPLAY" \
    --env="QT_X11_NO_MITSHM=1" \
    --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
    -v $PWD/docker/ddsconfig.xml:/ddsconfig.xml \
    -v $PWD:/bcr_ws/src/ \
    bcr_arm:humble-fortress \
    /bin/bash -c "cd /bcr_ws && rosdep install -i --from-path src --rosdistro humble -y && . /opt/ros/humble/setup.bash && colcon build && exec bash"

# Disable X11 forwarding after container stops
xhost -local:docker
