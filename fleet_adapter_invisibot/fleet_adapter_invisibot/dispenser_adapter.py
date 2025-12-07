import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, HistoryPolicy, ReliabilityPolicy
import sys
import argparse
import yaml
import json
import threading
import time
import requests

from rmf_fleet_msgs.msg import FleetState
from rmf_dispenser_msgs.msg import DispenserState, DispenserRequest, DispenserResult
from rmf_ingestor_msgs.msg import IngestorState, IngestorRequest, IngestorResult

class WorkcellNode(Node):
    """
    Workcell device in RMF network.
    Handles ROS 2 communication to receive requests, send status updates and responses.
    """

    def __init__(self, workcell_type, workcell_name, workcell_guid):
        super().__init__(workcell_name)
        self.get_logger().info(f"Initializing {workcell_name} adapter...")
        # Initialize member variables
        self._guid = workcell_guid
        self._workcell_type = workcell_type
        self._past_request_guids = []

        self._state = DispenserState()
        # Publishers and Subscribers
        self._request_sub = self.create_subscription(
            DispenserRequest,
            "/dispenser_requests",
            self.request_callback,
            QoSProfile(history=HistoryPolicy.KEEP_LAST, depth=10, reliability=ReliabilityPolicy.RELIABLE)
        )
        self._state_pub = self.create_publisher(
            DispenserState,
            "/dispenser_states",
            10
        )
        self._result_pub = self.create_publisher(
            DispenserResult,
            "/dispenser_results",
            10
        )

        # Initialize workcell state
        self._state.time = (self.get_clock().now().to_msg())
        self._state.guid = self._guid
        self._state.mode = DispenserState.IDLE
        self._state.request_guid_queue = []

        self._running = True
        # Start thread to update and publish workcell state
        self._state_lock = threading.Lock()  # Create a lock
        self._state_thread = threading.Thread(target=self.update_and_publish_state)
        self._state_thread.start()

        # Start thread to manage requests
        self._requests_queue = []
        self._requests_queue_lock = threading.Lock()
        self._requests_queue_thread = threading.Thread(target=self.handle_requests)
        self._requests_queue_thread.start()

    def make_response(self, status: int, request_guid: str, guid: str):
        """Makes a Result message of the corresponding type."""
        if self._workcell_type == "dispenser":
            response = DispenserResult()
        elif self._workcell_type == "ingestor":
            response = IngestorResult()
        response.time = self._state.time
        response.request_guid = request_guid
        response.source_guid = guid
        response.status = status
        return response

    def send_response(self, status: int, request_guid: str):
        """Sends a Result message."""
        response = self.make_response(status, request_guid, self._guid)
        self.get_logger().info(f"Publishing to result topic  : {response}")
        self._result_pub.publish(response)

    def request_callback(self, msg):
        """Callback for Request messages."""
        self.get_logger().warn(f"Received dispenser request...")
        # Check if request is for self
        if self._guid == msg.target_guid:
            # Check if task has been completed previously
            with self._requests_queue_lock:
                if msg.request_guid in self._past_request_guids:
                    self.get_logger().warn(f"Request already succeeded: [{msg.request_guid}]")
                    self.send_response(DispenserResult.SUCCESS, msg.request_guid)
                elif msg in self._requests_queue:
                    self.get_logger().warn(f"Request already in queue: [{msg.request_guid}]")
                else:
                    self.get_logger().info(f"Received new request: {msg}")
                    with self._state_lock:
                        self._state.request_guid_queue.append(msg.request_guid)
                    self._requests_queue.append(msg)
                    self.send_response(DispenserResult.ACKNOWLEDGED, msg.request_guid)
        else:
            self.get_logger().warn(f"No matching target_guid found for {msg.target_guid}...")

        
    def handle_requests(self):
        """Handles requests in requests queue."""
        self.get_logger().info("Starting thread to handle requests")
        while self._running:
            if self._requests_queue:
                with self._requests_queue_lock:
                    current_request = self._requests_queue[0]
                """Perform action"""
                self.get_logger().info(f"Handling request: {current_request}") 
                with self._state_lock:
                    self._state.mode = DispenserState.BUSY

                # Bring up the app to confirm user confirmation.
                self.get_logger().warn("SETTING APP TO TRUE")
                self.set_app_status(should_app_be_up=True)
                # Wait for app status to update
                is_waiting_for_user_acknowledgment = self.get_app_status
                while not is_waiting_for_user_acknowledgment:
                    is_waiting_for_user_acknowledgment = self.get_app_status()
                    time.sleep(1)

                # Wait for user to acknowledge before informing RMF of workcell SUCCESS state.
                start_time = time.time()
                while is_waiting_for_user_acknowledgment:
                    current_time = time.time()
                    elapsed_time = current_time - start_time
                    if elapsed_time > 30:
                        self.get_logger().warn(f"[dispensor] - Timeout reached. Moving on...") 
                        is_waiting_for_user_acknowledgment = False
                        break
                    is_waiting_for_user_acknowledgment = self.get_app_status()
                    self.get_logger().info(f"[dispensor] - Waiting for user acknowledgement...") 
                    time.sleep(5)

                if not is_waiting_for_user_acknowledgment:
                    with self._requests_queue_lock:
                        self._requests_queue.pop(0)
                    self._past_request_guids.append(current_request.request_guid)
                    self.send_response(DispenserResult.SUCCESS, current_request.request_guid)
                else:
                    self.send_response(DispenserResult.FAILED, current_request.request_guid)
                with self._state_lock:
                    self._state.request_guid_queue.remove(current_request.request_guid)
                    self._state.mode = DispenserState.IDLE

    def get_app_status(self) -> bool:
        # DEBUG
        return self.is_app_up

    def set_app_status(self, should_app_be_up: bool):
        self.is_app_up = should_app_be_up

    def update_and_publish_state(self):
        """Updates state time and publishes the State message continuously."""
        self.get_logger().info("Starting thread to publish workcell state")
        while self._running:
            with self._state_lock:
                self._state.time = (self.get_clock().now().to_msg())
                self._state_pub.publish(self._state)
                # self.get_logger().info(f"Current state is {self._state}")
            time.sleep(1)

    def destroy_node(self):
        """Override destroy_node to stop the thread gracefully."""
        self._running = False
        self._state_thread.join()  # Wait for the thread to finish
        self._requests_queue_thread.join()
        super().destroy_node()

def main(argv=sys.argv):
    rclpy.init(args=argv)
    args_without_ros = rclpy.utilities.remove_ros_args(argv)
    parser = argparse.ArgumentParser(
        prog="fleet_adapter",
        description="Configure and spin up the workcell adapter")
    parser.add_argument("-c", "--config_file", type=str, required=True,
                        help="Path to the config.yaml file")
    args = parser.parse_args(args_without_ros[1:])
  
    try:
        config_path = args.config_file
        # Load config_yaml
        with open(config_path, "r") as f:
            # config_yaml = yaml.safe_load(f)
            workcell_type = "dispenser"
            workcell_name = "invisibot_dispenser_workcell"
            workcell_guid = "invisibot_dispenser"
        workcell_node = WorkcellNode(
            workcell_type=workcell_type,
            workcell_name=workcell_name,
            workcell_guid=workcell_guid
            )
        rclpy.spin(workcell_node)
    except KeyboardInterrupt:
        pass
    finally:
        rclpy.try_shutdown()
        workcell_node.destroy_node()


if __name__ == '__main__':
    main(sys.argv)