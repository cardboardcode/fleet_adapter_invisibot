# Copyright 2021 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
import time
import requests
from urllib.error import HTTPError

'''
    The RobotAPI class is a wrapper for API calls to the robot. Here users
    are expected to fill up the implementations of functions which will be used
    by the RobotCommandHandle. For example, if your robot has a REST API, you
    will need to make http request calls to the appropriate endpoints within
    these functions.
'''


class RobotAPI:
    # The constructor below accepts parameters typically required to submit
    # http requests. Users should modify the constructor as per the
    # requirements of their robot's API
    def __init__(self, config_yaml, logger):
        self.logger = logger
        self.prefix = config_yaml['prefix']
        self.timeout = 5.0
        self.debug = False

        print(f"self.is_able_to_connect() = {self.is_able_to_connect()}")
        while not self.is_able_to_connect():
            print(f"self.is_able_to_connect() = {self.is_able_to_connect()}")
            self.logger.warn(f"Failed to connect to invisibot. Reattempting after 5 seconds...")
            time.sleep(5)

    def is_able_to_connect(self) -> bool:
        ''' Return True if connection to the robot API server is successfull'''
        path=f"{self.prefix}/status"
        try:
            response = requests.get(path)
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

            if response.status_code == 200:
                return True
            else:
                return False
        except requests.exceptions.ConnectionError as e:
            print(f"Error: Could not connect to the server at {path}. Please ensure the server is running.")
            return False
        except requests.exceptions.Timeout:
            print(f"Error: The request to {path} timed out.")
            return False
        except requests.exceptions.RequestException as e:
            print(f"An unexpected error occurred: {e}")
            return False

    def navigate(
        self,
        robot_name: str,
        pose,
        map_name: str,
        speed_limit=0.0
    ):
        ''' Request the robot to navigate to pose:[x,y,theta] where x, y and
            and theta are in the robot's coordinate convention. This function
            should return True if the robot has accepted the request,
            else False '''
        url = self.prefix + f"/navigate_to_pose?robot_name={robot_name}"

        headers = {'Content-Type': 'application/json'}
        self.logger.warn(f"Sending Navigation Goal...")

        payload = {
          "timestamp": 0,
          "x": pose[0],
          "y": pose[1],
          "yaw": pose[2],
          "obey_approach_speed_limit": False,
          "approach_speed_limit": speed_limit,
          "level_name": map_name,
          "index": 0
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            
            if response.status_code == 200:
                self.logger.info(f"Response Body: {response.text}")
                return True

            self.logger.info(f"Response Body: {response.text}")
        except HTTPError as http_err:
            self.logger.error(f"HTTP error: {http_err}")
        except Exception as err:
            self.logger.error(f"In [navigate]: Other error: {err}")
        return False

    def start_activity(
        self,
        robot_name: str,
        activity: str,
        label: str
    ):
        ''' Request the robot to begin a process. This is specific to the robot
        and the use case. For example, load/unload a cart for Deliverybot
        or begin cleaning a zone for a cleaning robot.
        Return True if process has started/is queued successfully, else
        return False '''
        # ------------------------ #
        # IMPLEMENT YOUR CODE HERE #
        # ------------------------ #
        return False

    def stop(self, robot_name: str) -> bool:
        ''' Command the robot to stop.
            Return True if robot has successfully stopped. Else False. '''
        path="http://localhost:8080/stop"
        try:
            response = requests.post(path)

            # Check for a 200 OK status explicitly
            if response.status_code == 200:
                return True
            else:
                return False

        except requests.exceptions.ConnectionError as e:
            print(f"Error: Could not connect to the server at {path}. Please ensure the server is running.")
            return False
        except requests.exceptions.Timeout:
            print(f"Error: The POST request to {path} timed out.")
            return False
        except requests.exceptions.RequestException as e:
            print(f"An unexpected error occurred during the POST request: {e}")
            return False

    def change_map(self, robot_name: str, map_name: str):
        ''' Command the robot to change map.
            Return True if robot has successfully changed map. Else False. '''
        path=f"http://localhost:8080/map_switch?robot_name={robot_name}&map={map_name}"
        try:
            response = requests.post(path)

            # Check for a 200 OK status explicitly
            if response.status_code == 200:
                return True
            else:
                return False

        except requests.exceptions.ConnectionError as e:
            print(f"Error: Could not connect to the server at {path}. Please ensure the server is running.")
            return False
        except requests.exceptions.Timeout:
            print(f"Error: The POST request to {path} timed out.")
            return False
        except requests.exceptions.RequestException as e:
            print(f"An unexpected error occurred during the POST request: {e}")
            return False

    def position(self, robot_name: str):
        ''' Return [x, y, theta] expressed in the robot's coordinate frame or
        None if any errors are encountered '''
        robot_status = self.get_robot_status()
        if robot_status:
            robot_pos = [robot_status["data"]["position"]["x"], robot_status["data"]["position"]["y"], robot_status["data"]["position"]["yaw"]]
            return robot_pos
        else:
            return None

    def battery_soc(self, robot_name: str):
        ''' Return the state of charge of the robot as a value between 0.0
        and 1.0. Else return None if any errors are encountered. '''
        robot_status = self.get_robot_status()
        if robot_status:
            return float(robot_status["data"]["battery"]/100.0)
        else:
            return None

    def map(self, robot_name: str):
        ''' Return the name of the map that the robot is currently on or
        None if any errors are encountered. '''
        robot_status = self.get_robot_status()
        if robot_status:
            return robot_status["data"]["map_name"]
        else:
            return None

    def is_command_completed(self):
        ''' Return True if the robot has completed its last command, else
        return False. '''
        robot_status = self.get_robot_status()
        if robot_status:
            return robot_status["data"]["completed_request"]
        else:
            return True

    def get_robot_status(self):
        path="http://localhost:8080/status"
        headers = {
            "accept": "application/json"
        }
        try:
            response = requests.get(path, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
            return response.json()
        except requests.exceptions.ConnectionError as e:
            print(f"Error: Could not connect to the server at {path}. Please ensure the server is running.")
            return None
        except requests.exceptions.Timeout:
            print(f"Error: The request to {path} timed out.")
            return None
        except requests.exceptions.RequestException as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def get_data(self, robot_name: str):
        ''' Returns a RobotUpdateData for one robot if a name is given. Otherwise
        return a list of RobotUpdateData for all robots. '''
        map = self.map(robot_name)
        position = self.position(robot_name)
        battery_soc = self.battery_soc(robot_name)
        if not (map is None or position is None or battery_soc is None):
            return RobotUpdateData(robot_name, map, position, battery_soc)
        return None


class RobotUpdateData:
    ''' Update data for a single robot. '''
    def __init__(self,
                 robot_name: str,
                 map: str,
                 position: list[float],
                 battery_soc: float,
                 requires_replan: bool | None = None):
        self.robot_name = robot_name
        self.position = position
        self.map = map
        self.battery_soc = battery_soc
        self.requires_replan = requires_replan
