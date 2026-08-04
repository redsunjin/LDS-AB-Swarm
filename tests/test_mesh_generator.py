import unittest
import numpy as np
from src.core.mesh_generator import ThreatTrajectory, MeshGenerator

class TestMeshGenerator(unittest.TestCase):
    def test_linear_mesh_generation(self):
        trajectory = ThreatTrajectory.create_linear(start_pos=[100.0, 0.0, 50.0], velocity=[-20.0, 0.0, 0.0])
        generator = MeshGenerator(default_spacing=4.0)

        # At t=2.0s, predicted position should be [60.0, 0.0, 50.0]
        nodes = generator.generate_mesh(trajectory, time_to_intercept=2.0, grid_shape=(3, 3))
        self.assertEqual(len(nodes), 9)

        # The center node of 3x3 (index 4) should be at [60, 0, 50]
        center_node = nodes[4]
        np.testing.assert_allclose(center_node, [60.0, 0.0, 50.0], atol=1e-5)

    def test_curved_mesh_generation(self):
        # Weaving trajectory with sinusoidal Y component
        trajectory = ThreatTrajectory.create_weaving_sinusoidal(
            start_pos=[150.0, 0.0, 20.0],
            base_velocity=[-30.0, 0.0, 0.0],
            amplitude=5.0
        )
        generator = MeshGenerator(default_spacing=5.0)

        # 5x5 grid with 2 depth layers = 50 nodes
        nodes = generator.generate_mesh(trajectory, time_to_intercept=1.5, grid_shape=(5, 5), depth_layers=2)
        self.assertEqual(nodes.shape, (50, 3))

if __name__ == "__main__":
    unittest.main()
