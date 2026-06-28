#!/usr/bin/env bash

CONFIG_FILE="/fleet_adapter_invisibot_ws/src/fleet_adapter_invisibot/config.yaml"
NAV_GRAPH_FILE="/fleet_adapter_invisibot_ws/src/fleet_adapter_invisibot/nav_graph.yaml"
TRAJECTORY_SERVER_URL="ws://localhost:8000/_internal"

docker run -it -d \
	--name fleet_adapter_invisibot_c \
	--restart unless-stopped \
	--network host \
	-e RCL_LOG_LEVEL=debug \
	-e RCUTILS_COLORIZED_OUTPUT=1 \
	-e RMW_IMPLEMENTATION=rmw_cyclonedds_cpp \
	-v ./fleet_adapter_invisibot/config.yaml:$CONFIG_FILE \
    -v ./fleet_adapter_invisibot/nav_graph.yaml:$NAV_GRAPH_FILE \
ghcr.io/cardboardcode/fleet_adapter_invisibot:bugfix_stalled_registration bash -c \
"source /ros_entrypoint.sh && \
ros2 launch fleet_adapter_invisibot fleet_adapter.launch.xml \
config_file:=$CONFIG_FILE \
nav_graph_file:=$NAV_GRAPH_FILE \
server_uri:=$TRAJECTORY_SERVER_URL \
use_sim_time:=true"

unset CONFIG_FILE NAV_GRAPH_FILE