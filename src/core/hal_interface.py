from abc import ABC, abstractmethod
import numpy as np
from typing import Dict, Any
from src.simulator.drone import Drone
from src.core.dsp_protocol import DefensiveSwarmProtocol

class DroneHALInterface(ABC):
    """
    Hardware Abstraction Layer (HAL) Interface for Open Device Support.
    Provides unified API for PX4, ArduPilot, Generic FPV, and Simulation platforms.
    """
    def __init__(self, drone_id: int):
        self.drone_id = drone_id
        self.seq = 0

    @abstractmethod
    def send_setpoint_accel(self, accel: np.ndarray) -> bytes:
        """Sends 3D acceleration thrust setpoint vector to flight controller."""
        pass

    @abstractmethod
    def send_popup_launch_command(self) -> bytes:
        """Triggers cold gas pneumatic pop-up ejection and motor arming."""
        pass

    @abstractmethod
    def get_telemetry(self) -> Dict[str, Any]:
        """Returns standard telemetry dictionary [status, pos, vel, battery]."""
        pass


class SimulatedHALAdapter(DroneHALInterface):
    """HAL Adapter for physics simulation environment."""
    def __init__(self, drone: Drone):
        super().__init__(drone.id)
        self.drone = drone

    def send_setpoint_accel(self, accel: np.ndarray) -> bytes:
        self.seq += 1
        # Encode as open DSP binary packet
        return DefensiveSwarmProtocol.encode_thrust_vector(self.seq, self.drone_id, accel)

    def send_popup_launch_command(self) -> bytes:
        self.seq += 1
        return b"\x44\x53\x05\x00\x01\x00\x00"

    def get_telemetry(self) -> Dict[str, Any]:
        status_code = 1 if self.drone.status == "active" else 0
        return {
            "platform": "SIMULATED_HAL",
            "drone_id": self.drone_id,
            "status": self.drone.status,
            "position": self.drone.position.copy(),
            "velocity": self.drone.velocity.copy(),
            "battery_mv": 16800  # 4S LiPo voltage
        }


class PX4HALAdapter(DroneHALInterface):
    """HAL Adapter for PX4 Autopilot via MAVLink Offboard protocol."""
    def __init__(self, drone_id: int, mavlink_sysid: int = 1):
        super().__init__(drone_id)
        self.mavlink_sysid = mavlink_sysid
        self.arm_state = False

    def send_setpoint_accel(self, accel: np.ndarray) -> bytes:
        self.seq += 1
        # Formats DSP packet mapped to MAVLink SET_POSITION_TARGET_LOCAL_NED
        return DefensiveSwarmProtocol.encode_thrust_vector(self.seq, self.drone_id, accel)

    def send_popup_launch_command(self) -> bytes:
        self.arm_state = True
        self.seq += 1
        return b"\x44\x53\x05\x00\x01\x00\x01"  # Armed

    def get_telemetry(self) -> Dict[str, Any]:
        return {
            "platform": "PX4_AUTOPILOT_MAVLINK",
            "drone_id": self.drone_id,
            "sysid": self.mavlink_sysid,
            "armed": self.arm_state,
            "mode": "OFFBOARD"
        }


class ArduPilotHALAdapter(DroneHALInterface):
    """HAL Adapter for ArduPilot Autopilot via MAVLink GUIDED mode."""
    def __init__(self, drone_id: int):
        super().__init__(drone_id)

    def send_setpoint_accel(self, accel: np.ndarray) -> bytes:
        self.seq += 1
        return DefensiveSwarmProtocol.encode_thrust_vector(self.seq, self.drone_id, accel)

    def send_popup_launch_command(self) -> bytes:
        self.seq += 1
        return b"\x44\x53\x05\x00\x01\x00\x01"

    def get_telemetry(self) -> Dict[str, Any]:
        return {
            "platform": "ARDUPILOT_GUIDED_MAVLINK",
            "drone_id": self.drone_id,
            "mode": "GUIDED"
        }
