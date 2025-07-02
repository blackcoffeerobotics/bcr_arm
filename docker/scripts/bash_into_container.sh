#!/bin/bash
xhost +local:root

docker exec -it --env="DISPLAY" --env="QT_X11_NO_MITSHM=1" bcr_arm_container bash

xhost -local:root