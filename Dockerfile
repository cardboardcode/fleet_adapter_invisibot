ARG ROS_DISTRO=jazzy
FROM cardboardcode/rmf:$ROS_DISTRO-ros-core
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    cmake \
  && pip3 install flask-socketio fastapi uvicorn nudged --break-system-packages \
  && rm -rf /var/lib/apt/lists/*

# Copy in the fleet_adapter_tb3 ROS2 package.
WORKDIR /fleet_adapter_invisibot_ws
COPY fleet_adapter_invisibot src/fleet_adapter_invisibot

# Compile the ROS 2 package.
RUN . /opt/ros/$ROS_DISTRO/setup.sh \
  && colcon build --mixin clang lld --merge-install --cmake-args -DCMAKE_BUILD_TYPE=Release

# Add sourcing statement to /ros_entrypoint.sh
RUN sed -i '$isource "/fleet_adapter_invisibot_ws/install/setup.bash"' /ros_entrypoint.sh

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]

