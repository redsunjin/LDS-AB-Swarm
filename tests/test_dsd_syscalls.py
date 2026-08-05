import unittest
import numpy as np
from src.core.dsd_syscalls import DSDOSKernelSyscalls

class TestDSDOSKernelSyscalls(unittest.TestCase):
    def test_sys_deploy_mesh(self):
        syscalls = DSDOSKernelSyscalls(num_drones=50)
        nodes = syscalls.sys_deploy_mesh(shape_type="tilted", depth_layers=2, pitch_deg=20.0)

        self.assertEqual(len(nodes), 50)
        self.assertFalse(np.isnan(nodes).any())

    def test_sys_get_neighbor_telemetry(self):
        syscalls = DSDOSKernelSyscalls()
        positions = {
            1: np.array([20.0, 0.0, 25.0]),
            2: np.array([20.0, 5.0, 25.0]),
            3: np.array([20.0, 50.0, 25.0])  # Far away (>30m)
        }

        neighbors = syscalls.sys_get_neighbor_telemetry(1, positions)
        self.assertEqual(len(neighbors), 1)
        self.assertEqual(neighbors[0]["drone_id"], 2)

    def test_sys_execute_interception(self):
        syscalls = DSDOSKernelSyscalls()
        target_vec = np.array([-1.0, 0.0, 0.0])
        pkt = syscalls.sys_execute_interception(target_vec)

        self.assertIsInstance(pkt, bytes)
        self.assertGreater(len(pkt), 10)

if __name__ == "__main__":
    unittest.main()
