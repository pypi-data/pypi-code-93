import math
from logging import getLogger, NullHandler, INFO
import pprint
from pydantic import BaseModel
import psutil
import os
import time
import socket

import docker
from docker import from_env as docker_client, DockerClient
from docker.models import containers, networks
from docker.errors import NotFound, ImageNotFound
from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal, Command, APIException
from numpy import array
import numpy as np
from pymavlink import mavutil

from geopy import Point
from geopy.distance import distance, geodesic

from .models import Mission, FenceType, Waypoint, ArduStackConfig, Rect, Geofence
import subprocess
import sys

from typing import List, Tuple

logger = getLogger("ardustack")
np.set_printoptions(suppress=True)

def _container_ready(container: containers.Container) -> bool:
    """Returns whether or not the container is ready

    Args:
        container (containers.Container): Container object created by the ArduStack

    Returns:
        bool: True if container status is running, False in all other cases
    """
    try:
        container.reload()
        return container.status == "running"
    except NotFound as nf:
        return False
    
    return False

def find_open_tcp_port() -> int:
    """Binds to a socket port selected by the OS, and returns the port number

    Returns:
        int: Open TCP port at which the ArduPilot SITL can bind
    """
    s = socket.socket()
    s.bind(('', 0))
    return int(s.getsockname()[1])

class ArduStack:
    def __init__(self, prefix: str, config: ArduStackConfig):
        logger.setLevel(INFO if config.verbose else WARN)

        self.config = config
        self.vehicle = None
        self.prefix = prefix
        self.t0 = None
        self.flight_log = []
        self.eta = {}
        self.groundspeed = 10
        self.wait_factor  = 6
        self.wp_1_neighbourhood = None
        self.wp_2_neighbourhood = None
        
        self.master_timer = 200

    def _start_container(self, mission: Mission) -> Tuple[containers.Container, str]:
        """Starts the ArduPilot SITL container for the mission

        Args:
            mission (Mission): Mission object provided by mission_factory

        Returns:
            containers.Container: Docker container option
            connnection_string: str: Connection string for the connected port
        """
        home_location = mission.waypoints[0]
        docker_env = {
            'LAT': home_location.lat,
            'LON': home_location.lon,
            'ALT': 0,
            'SPEEDUP': self.config.simulation_speedup
        }
        
        open_port = find_open_tcp_port()

        client = docker_client()
        nproc_limit = docker.types.Ulimit(name='nproc', soft=98304, hard=98304)
        container = client.containers.run("registry.gitlab.com/sbtg/ardupilot-falsifications", tty=True, ports={'5760/tcp': open_port}, 
                    name=self.prefix, environment=docker_env, detach=True,
                    restart_policy={"Name": "on-failure", "MaximumRetryCount": 5},
                    ulimits=[nproc_limit])
        
        while not _container_ready(container):
            logger.info("Waiting for container to start")
            time.sleep(1)

        time.sleep(3)
        
        connection_string = self.config.base_string + ":{}".format(open_port)
        
        return container, connection_string

    def _setup_mission_geofences(self, geofences: List[Geofence]) -> None:
        """Constructs corresponding MAVLink commands and initializes the geofence for given mission

        Args:
            geofences (List[Geofence]): List of geofences from the mission object
        """
        for geofence in geofences:
            fence_type = geofence.fence_type
            vertice_count = len(geofence.vertices)
            for vertice in geofence.vertices:
                if fence_type == FenceType.INCLUSIVE:
                    # MAV_CMD_NAV_FENCE_POLYGON_VERTEX_INCLUSION
                    msg = self.vehicle.message_factory.command_long_encode(
                        0, 0,
                        mavutil.mavlink.MAV_CMD_NAV_FENCE_POLYGON_VERTEX_INCLUSION, 0,
                        vertice_count,
                        1,
                        0,
                        0,
                        vertice.lat,
                        vertice.lon,
                        0
                    )
                    self.vehicle.send_mavlink(msg)
                else:
                    # MAV_CMD_NAV_FENCE_POLYGON_VERTEX_EXCLUSION
                    msg = self.vehicle.message_factory.command_long_encode(
                        0, 0,
                        mavutil.mavlink.MAV_CMD_NAV_FENCE_POLYGON_VERTEX_EXCLUSION, 0,
                        vertice_count,
                        1,
                        0,
                        0,
                        vertice.lat,
                        vertice.lon,
                        0
                    )
                    self.vehicle.send_mavlink(msg)

        # Enable fence
        time.sleep(1)
        self.vehicle.parameters['FENCE_AUTOENABLE'] = 1
        self.vehicle.parameters['FENCE_TYPE'] = 2
        self.vehicle.parameters['FENCE_ACTION'] = 2
        self.vehicle.parameters['FENCE_TOTAL'] = 4
        self.vehicle.parameters['FENCE_MARGIN'] = 5

        msg = self.vehicle.message_factory.command_long_encode(
            0, 0,
            mavutil.mavlink.MAV_CMD_DO_FENCE_ENABLE, 0,
            1, 0, 0, 0, 0, 0, 0
        )
        self.vehicle.send_mavlink(msg)

        return

    def _setup_mission_waypoints(self, waypoints: List[Waypoint]) -> None:
        """Constructs and sends the mission using a set of MAVLink commands

        Args:
            waypoints (List[Waypoint]): List of waypoints from the mission object
        """
        cmds = self.vehicle.commands
        
        logger.info("Clearing existing commands, starting clean")
        cmds.clear()

        logger.info("Adding new commands")

        # Take off command
        cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 0, 10))

        for waypoint in waypoints:
            cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, waypoint.lat, waypoint.lon, waypoint.alt))

        # dummy waypoint using the last wp for callback to destination
        cmds.add(Command( 0, 0, 0, mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, waypoint.lat, waypoint.lon, waypoint.alt))

        logger.info("Uploading commands")
        cmds.upload()
        
        return

    def _arm_and_takeoff(self, aTargetAltitude: float):
        """Performs pre-arm checks, arms the motors and takes off to the target altitude

        Args:
            aTargetAltitude (float): Target altitude in meters

        Returns:
            [type]: [description]
        """

        logger.info("Basic pre-arm checks")
        while not self.vehicle.is_armable:
            logger.info(self.vehicle.mode.name)
            logger.info(" Waiting for vehicle to initialise...")
            time.sleep(1)

        logger.info("Arming motors")
        # Copter should arm in GUIDED mode
        self.vehicle.mode = VehicleMode("GUIDED")
        self.vehicle.armed = True

        tmp_t0 = time.time()
        while not self.vehicle.armed:
            logger.info(self.vehicle.mode.name)
            logger.info(" Waiting for arming...")
            time.sleep(1)
            if time.time() - tmp_t0 > self.master_timer:
                return False

        self.t0 = time.time()

        logger.info("Taking off!")
        self.vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

        # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command 
        #  after Vehicle.simple_takeoff will execute immediately).
        while True:
            logger.info(" Altitude: {}".format(self.vehicle.location.global_relative_frame.alt))      
            if self.vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95: #Trigger just below target alt.
                logger.info("Reached target altitude")
                break
            time.sleep(1)

        return True

    def calculate_neighbourhoods(self, waypoint: Waypoint) -> dict:
        """Calculates the neighbourhood for each waypoint in a mission

        Args:
            waypoint (Waypoint): Waypoint object from the mission

        Returns:
            dict: Contains the neighbourhood defined in the format of a dictionary ({lat: {min, max}, lon: {min, max}})
        """
        wp = Point(waypoint.lat, waypoint.lon)
        top_middle_point = distance(meters=self.config.waypoint_distance_threshold/2).destination(wp, 0)
        top_right_point = distance(meters=self.config.waypoint_distance_threshold/2).destination(top_middle_point, 90)
        top_left_point = distance(meters=self.config.waypoint_distance_threshold/2).destination(top_middle_point, -90)
        bottom_right_point = distance(meters=self.config.waypoint_distance_threshold).destination(top_right_point, 180)
        bottom_left_point = distance(meters=self.config.waypoint_distance_threshold).destination(top_left_point, 180)

        return {
            'lat': {
                'min': bottom_left_point.latitude,
                'max': top_left_point.latitude
            },
            'lon': {
                'min': bottom_left_point.longitude,
                'max': bottom_right_point.longitude
            }
        }

    @staticmethod
    def get_distance_metres(location1: Point, location2: Point) -> float:
        """Calculates the geodesic distance between two points (point 1 and point 2)

        Args:
            location1 (Point): Point 1 (must contain lat, lon fields)
            location2 (Point): Point 2 (must contain lat, lon fields)

        Returns:
            float: Distance between two points in meters
        """
        pt1 = Point(location1.lat, location1.lon)
        pt2 = Point(location2.lat, location2.lon)
        return distance(pt1, pt2).m

    
    def _distance_to_current_waypoint(self) -> float:
        """Calculates the distance between the current location and the next waypoint

        Returns:
            float: Distance in meters
        """
        nextwaypoint = self.vehicle.commands.next
        if nextwaypoint == 0:
            return None
        missionitem = self.vehicle.commands[nextwaypoint-1] #commands are zero indexed
        lat = missionitem.x
        lon = missionitem.y
        alt = missionitem.z
        targetWaypointLocation = LocationGlobalRelative(lat,lon,alt)
        distancetopoint = self.get_distance_metres(self.vehicle.location.global_frame, targetWaypointLocation)
        return distancetopoint
    
    def _commence_and_monitor_mission(self, mission: Mission) -> None:
        """Starts the mission and monitors the progress

        Args:
            mission (Mission): Mission object from mission factory
        """
        # From Copter 3.3 you will be able to take off using a mission item. Plane must take off using a mission item (currently).
        retval = self._arm_and_takeoff(mission.waypoints[0].alt)
        
        if not retval:
            self.hard_reset()

        logger.info("Starting mission")
        # Reset mission set to first (0) waypoint
        self.vehicle.commands.next = 0
        self.vehicle.groundspeed = self.groundspeed

        # Set mode to AUTO to start mission
        self.vehicle.mode = VehicleMode("AUTO")

        while True:
            nextwaypoint = self.vehicle.commands.next
            dist = self._distance_to_current_waypoint()

            if dist is not None:
                if self.vehicle.commands.next not in self.eta:
                    self.eta.update({self.vehicle.commands.next: {
                        'eta': (dist / self.groundspeed) * self.wait_factor,
                        'clk': 0,
                        'dt': time.time()
                    }})
            
            elapsed = "NA"
            eta = "NA"
            if self.vehicle.commands.next in self.eta:
                d = self.eta[self.vehicle.commands.next]
                d['clk'] = time.time() - self.eta[self.vehicle.commands.next]['dt']
                self.eta.update({self.vehicle.commands.next: d})
                if self.eta[self.vehicle.commands.next]['clk'] > self.eta[self.vehicle.commands.next]['eta']:
                    self.vehicle.commands.next += 1

                elapsed = self.eta[self.vehicle.commands.next]['clk']
                eta = self.eta[self.vehicle.commands.next]['eta']

            logger.info('Distance to waypoint (%s): %s, Elapsed: %s, ETA: %s' % (nextwaypoint, dist, elapsed, eta))
            
            if nextwaypoint == len(mission.waypoints) + 1: #Dummy waypoint - as soon as we reach waypoint 4 this is true and we exit.
                logger.info("Exit 'standard' mission when start heading to final waypoint")
                break
            time.sleep(8)

        logger.info('Return to launch')
        self.vehicle.mode = VehicleMode("RTL")

    def _location_callback(self, v, attr, msg):
        """Location callback
        Used to store the flight telemetry data in memory - since ArduPilot does not provide a telemetry log file to read from

        Args:
            v (dronekit.Vehicle): Vehicle
            attr (str): Attribute name
            msg (message): received message
        """
        if self.t0 is not None:
            self.flight_log.append({'ts': (time.time() - self.t0) * self.config.simulation_speedup, 'lat': msg.lat, 'lon': msg.lon, 'alt': msg.alt})
        
    def _read_flight_log(self):
        """Read flight log from within memory

        Returns:
            Tuple(array, array): Tuple containing positions (lat, lon, alt) and timestamps corresponding to each location
        """
        positions = []
        timestamps = []

        for log in self.flight_log:
            positions.append([log['lat'], log['lon'], log['alt']])
            timestamps.append(log['ts'])

        return array(positions), array(timestamps)

    def _get_fence_rect(self, fence: Geofence):
        """Generate fence rectangle using the Geofence provided by mission factory

        Args:
            fence (Geofence): Geofence for the mission

        Returns:
            Rect: Rectangle for robustness computation
        """
        vertices = fence.vertices

        lats = []
        lons = []
        for vertice in vertices:
            lats.append(vertice.lat)
            lons.append(vertice.lon)

        lat_min = np.amin(lats)
        lat_max = np.amax(lats)
        lon_min = np.amin(lons)
        lon_max = np.amax(lons)

        return Rect(x_min=lat_min, x_max=lat_max, y_min=lon_min, y_max=lon_max)

    def _calculate_distance(self, fence_rect: Rect, position: array) -> float:
        """Calculate distance between a point (position) and a rectangle (fence_rect)

        Args:
            fence_rect (Rect): No-fly zone rectangle
            position (array): Drone co-ordinate (lat, lon, alt)

        Returns:
            float: Distance
        """
        dx = np.amax([fence_rect.x_min - position[0], 0, position[0] - fence_rect.x_max])
        dy = np.amax([fence_rect.y_min - position[1], 0, position[1] - fence_rect.y_max])
        return math.sqrt(dx*dx + dy*dy)

    def _get_rob(self, positions: array, mission: Mission):
        """Calculate robustness values separately for the mission

        Args:
            positions (array): Drone trajectory (lat, lon, alt)
            mission (Mission): Mission object from mission factory

        Returns:
            [array]: Shortest distances between the no-fly zone and the drone location (-1 if there is a violation)
        """
        fence_rect = self._get_fence_rect(mission.geofences[0])
        distances = []
        for pos in positions:
            distances.append(self._calculate_distance(fence_rect, pos))
        distances = array(distances)
        distances[distances == 0] = -1
        return distances

    def _close(self):
        """Close drone object (works for ardupilot SITL and dronekit SITL)
        """
        if self.vehicle is not None:
            self.vehicle.close()

        if not self.config.use_dronekit_sitl:
            self.container.stop()
            self.container.remove(force=True)
        else:
            try:
                self.sitl.stop()
            except psutil.NoSuchProcess:
                pass

        os.system("pkill -9 apm")

    def _start_dk_sitl(self, mission):
        """Start DroneKit SITL instead of ArduPilot SITL

        Args:
            mission (Mission): Mission generated by the mission factory

        Returns:
            [dronekit_sitl.SITL]: Simulator in the loop object
        """
        import dronekit_sitl
        home_location = mission.waypoints[0]
        self.sitl = dronekit_sitl.start_default(lat=home_location.lat, lon=home_location.lon)

        return self.sitl

    def hard_reset(self):
        self._close()
        subprocess.Popen(["poetry", "run", "ardutest", "polar_mission_completion"], cwd=self.config.retry_working_dir, start_new_session=True)
        sys.exit(0)


    def execute(self, mission: Mission):
        """Execute mission using the Ardupilot SITL

        Args:
            mission (Mission): mission object created using the mission factory

        Returns:
            Tuple(positions, distances, timestamps): Trajectories and timestamps for the executed mission
        """
        retry_count = 0

        if not self.config.use_dronekit_sitl:
            self.container, self.config.connection_string = self._start_container(mission)
        else:
            import dronekit_sitl
            # home_location = mission.waypoints[0]
            # self.sitl = dronekit_sitl.start_default(lat=home_location.lat, lon=home_location.lon)
            self.sitl = self._start_dk_sitl(mission)
            self.config.connection_string = self.sitl.connection_string()

        logger.info("Connecting to {}".format(self.config.connection_string))

        try:
            self.vehicle = connect(self.config.connection_string, wait_ready=True, heartbeat_timeout=60)
        except APIException as ae:
            logger.info(ae)
            while retry_count < self.config.retries:
                logger.info("Retrying {}".format(retry_count))
                self._close()
                time.sleep(5)
                
                if not self.config.use_dronekit_sitl:
                    self.container, self.config.connection_string = self._start_container(mission)
                else:
                    self.sitl = self._start_dk_sitl(mission)
                    self.config.connection_string = self.sitl.connection_string()

                time.sleep(20)
                try:
                    self.vehicle = connect(self.config.connection_string, wait_ready=True, heartbeat_timeout=60)
                    logger.info(self.vehicle)
                    break
                except APIException as ae1:
                    logger.info(ae1)
                    pass
                
                if self.vehicle is not None:
                    break
                retry_count += 1
                
            if self.vehicle is None:
                self.hard_reset()

        self.vehicle.add_attribute_listener('location.global_frame', self._location_callback)

        # self._setup_mission_geofences(mission.geofences)
        self._setup_mission_waypoints(mission.waypoints)
        self._commence_and_monitor_mission(mission)
        logger.info("Closing drone object; cleaning up")
        self._close()
        positions, timestamps = self._read_flight_log()
        # distances = self._get_rob(positions, mission)
        distances = []

        return positions, distances, timestamps
