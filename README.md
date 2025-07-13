## **What Is This?**

A RMF Fleet Adapter that bridges interaction between Open-RMF and [invisibot](https://github.com/cardboardcode/invisibot).

## **Build**

```bash
docker build -t fleet_adapter_invisibot:jazzy .
```

## **Configuration(s)**
The `config.yaml` file contains important parameters for setting up the fleet adapter. There are three broad sections to this file:

1. **rmf_fleet** : containing parameters that describe the robots in this fleet
2. **fleet_manager** : containing configurations to connect to the robot's API in order to retrieve robot status and send commands from RMF
3. **reference_coordinates**: containing two sets of [x,y] coordinates that correspond to the same locations but recorded in RMF (`traffic_editor`) and robot specific coordinates frames respectively. These are required to estimate coordinate transformations from one frame to another. A minimum of 4 matching waypoints is recommended.

> Note: This fleet adapter uses the `nudged` python library to compute transformations from RMF to Robot frame and vice versa. If the user is aware of the `scale`, `rotation` and `translation` values for each transform, they may modify the code in `fleet_adapter.py` to directly create the `nudged` transform objects from these values.

## **Run**

```bash
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
```

## **Maintainer(s)**

- [Gary Bey](https://github.com/cardboardcode)