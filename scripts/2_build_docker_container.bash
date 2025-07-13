#!/usr/bin/env bash

docker run -it --rm \
	--name fleet_adapter_invisibot_c \
	--network host \
	-e RMW_IMPLEMENTATION=rmw_cyclonedds_cpp \
	-v ./fleet_adapter_invisibot/config.yaml:/fleet_adapter_invisibot_ws/src/fleet_adapter_invisibot/config.yaml \
    -v ./fleet_adapter_invisibot/nav_graph.yaml:/fleet_adapter_invisibot_ws/src/fleet_adapter_invisibot/nav_graph.yaml \
fleet_adapter_invisibot:jazzy bash -c \
"source /ros_entrypoint.sh && \
ros2 run fleet_adapter_invisibot fleet_adapter \
-c /fleet_adapter_invisibot_ws/src/fleet_adapter_invisibot/config.yaml \
-n /fleet_adapter_invisibot_ws/src/fleet_adapter_invisibot/nav_graph.yaml \
-s ws://localhost:8000/_internal"