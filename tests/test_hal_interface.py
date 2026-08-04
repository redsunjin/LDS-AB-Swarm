import unittest
import numpy as np
from src.simulator.drone import Drone
from src.core.hal_interface import SimulatedHALAdapter, PX4HALAdapter, ArduPilotHALAdapter

class TestHALInterface(unittest.TestCase):
    def test_simulated_hal_adapter(self):
        drone = Drone(id=1, position=np.array([10.0, 0.0, 5.0]))
        adapter = SimulatedHALAdapter(drone)

        pkt = adapter.send_setpoint_accel(np.array([5.0, 0.0, 0.0]))
        self.assertIsInstance(pkt, bytes)

        telem = adapter.get_telemetry()
        self.assertEqual(telem["platform"], "SIMULATED_HAL")
        self.assertEqual(telem["drone_id"], 1)

    def test_px4_hal_adapter(self):
        adapter = PX4HALAdapter(drone_id=2, mavlink_sysid=10)
        pkt = adapter.send_popup_launch_command()
        self.assertIsInstance(pkt, bytes)

        telem = adapter.get_telemetry()
        self.assertEqual(telem["platform"], "PX4_AUTOPILOT_MAVLINK")
        self.assertTrue(telem["armed"])

    def test_ardupilot_hal_adapter(self):
        adapter = ArduPilotHALAdapter(drone_id=3)
        telem = adapter.get_telemetry()
        self.assertEqual(telem["platform"], "ARDUPILOT_GUIDED_MAVLINK")

if __name__ == "__main__":
    unittest.main()
