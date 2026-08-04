import unittest
import numpy as np
from src.core.mesh_generator import ThreatTrajectory, MeshGenerator

class TestMultiLayerMeshGenerator(unittest.TestCase):
    def test_multi_layer_staggered_grid(self):
        trajectory = ThreatTrajectory.create_linear(start_pos=[150.0, 0.0, 30.0], velocity=[-30.0, 0.0, 0.0])
        generator = MeshGenerator(default_spacing=5.0)

        # 5x5 per layer x 2 depth layers = 50 nodes total
        nodes = generator.generate_mesh(
            trajectory, time_to_intercept=2.0, grid_shape=(5, 5), depth_layers=2, layer_stagger=True
        )

        self.assertEqual(nodes.shape, (50, 3))

        # Check distance between Layer 1 center and Layer 2 center along depth axis
        layer1_center = nodes[12]
        layer2_center = nodes[37]
        depth_dist = np.linalg.norm(layer1_center - layer2_center)
        self.assertGreater(depth_dist, 1.0)

    def test_tilted_barrier_angle(self):
        trajectory = ThreatTrajectory.create_linear(start_pos=[100.0, 0.0, 40.0], velocity=[-20.0, 0.0, 0.0])
        generator = MeshGenerator(default_spacing=6.0)

        # Generate tilted grid
        tilted_nodes = generator.generate_mesh(
            trajectory, time_to_intercept=2.0, grid_shape=(3, 3), pitch_offset_deg=25.0
        )

        # Center node should match predicted intercept position
        center_node = tilted_nodes[4]
        np.testing.assert_allclose(center_node, [60.0, 0.0, 40.0], atol=1e-4)

if __name__ == "__main__":
    unittest.main()
