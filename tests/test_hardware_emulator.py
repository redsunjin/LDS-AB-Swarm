import unittest
import numpy as np
from src.simulator.hardware_emulator import VirtualHardwareEmulationTestbed, VirtualDroneNode

class TestVirtualHardwareEmulator(unittest.TestCase):
    def test_virtual_drone_node_packet_handling(self):
        node = VirtualDroneNode(node_id=1, initial_pos=np.array([20.0, 0.0, 0.8]))
        accel = np.array([5.0, 0.0, 1.0])

        # Test DSP control packet dispatch
        testbed = VirtualHardwareEmulationTestbed(num_nodes=50)
        telem_map = testbed.dispatch_dsp_control_loop({1: accel, 2: accel})

        self.assertIn(1, telem_map)
        self.assertIn(2, telem_map)
        self.assertEqual(telem_map[1]["msg_type"], "HEARTBEAT")
        self.assertEqual(telem_map[1]["sender_id"], 1)

if __name__ == "__main__":
    unittest.main()
