ARG ROS_DISTRO=kilted

# ==========================================
# Builder
# ==========================================
FROM cardboardcode/rmf:$ROS_DISTRO-ros-core AS builder

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        cmake \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /fleet_adapter_invisibot_ws

COPY fleet_adapter_invisibot src/fleet_adapter_invisibot

RUN . /opt/ros/$ROS_DISTRO/setup.sh && \
    colcon build \
        --merge-install \
        --cmake-args \
        -DCMAKE_BUILD_TYPE=Release

# Remove build artifacts
RUN rm -rf \
    build \
    log \
    src

# ==========================================
# Runtime
# ==========================================
FROM cardboardcode/rmf:$ROS_DISTRO-ros-core

ENV DEBIAN_FRONTEND=noninteractive

RUN pip3 install --no-cache-dir \
        flask-socketio \
        uvicorn \
        nudged \
        --break-system-packages

COPY --from=builder \
    /fleet_adapter_invisibot_ws/install \
    /fleet_adapter_invisibot_ws/install

RUN sed -i '$isource "/fleet_adapter_invisibot_ws/install/setup.bash"' \
    /ros_entrypoint.sh

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]