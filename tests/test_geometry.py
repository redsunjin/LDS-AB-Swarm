import unittest
import numpy as np
from src.core.geometry import DynamicBarrierGeometry

class TestGeometry(unittest.TestCase):
    def test_intercept_plane_orientation(self):
        threat_pos = np.array([100.0, 0.0, 50.0])
        threat_vel = np.array([-50.0, 0.0, 0.0])  # Moving along -X
        time_to_intercept = 2.0

        center, u, v = DynamicBarrierGeometry.calculate_intercept_plane(threat_pos, threat_vel, time_to_intercept)

        # Expected center position: [100 - 100, 0, 50] = [0, 0, 50]
        np.testing.assert_allclose(center, [0.0, 0.0, 50.0], atol=1e-5)

        # u and v must be orthogonal to threat velocity (which is along X)
        self.assertLess(abs(np.dot(u, threat_vel)), 1e-5)
        self.assertLess(abs(np.dot(v, threat_vel)), 1e-5)
        self.assertLess(abs(np.dot(u, v)), 1e-5)

    def test_grid_nodes_count_and_spacing(self):
        threat_pos = np.array([200.0, 10.0, 30.0])
        threat_vel = np.array([-20.0, 0.0, 0.0])
        grid_size = (5, 5)
        spacing = 10.0

        nodes = DynamicBarrierGeometry.generate_3d_grid_nodes(
            threat_pos, threat_vel, time_to_intercept=3.0, grid_size=grid_size, spacing=spacing
        )

        self.assertEqual(len(nodes), 25)
        # Distance between adjacent nodes along row should match spacing
        dist = np.linalg.norm(nodes[0] - nodes[1])
        np.testing.assert_allclose(dist, spacing, atol=1e-4)

if __name__ == "__main__":
    unittest.main()
