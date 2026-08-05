import unittest
import numpy as np
from src.core.omnidirectional_barrier import OmnidirectionalBarrierEngine, Threat360Vector

class TestOmnidirectionalBarrierEngine(unittest.TestCase):
    def test_omni_cylindrical_perimeter_mesh(self):
        engine = OmnidirectionalBarrierEngine(base_center=np.array([20.0, 0.0, 20.0]))
        threats = [
            Threat360Vector(1, azimuth_deg=0.0, elevation_deg=0.0, distance_m=100.0, approach_velocity=np.array([-20, 0, 0])),
            Threat360Vector(2, azimuth_deg=180.0, elevation_deg=0.0, distance_m=100.0, approach_velocity=np.array([20, 0, 0]))
        ]

        nodes, mode = engine.generate_360_morphing_barrier(threat_vectors=threats, net_mode="OMNI_CYLINDRICAL_PERIMETER", num_drones=50)

        self.assertEqual(mode, "OMNI_CYLINDRICAL_PERIMETER")
        self.assertEqual(len(nodes), 50)
        self.assertFalse(np.isnan(nodes).any())

    def test_top_cover_umbrella_mesh(self):
        engine = OmnidirectionalBarrierEngine()
        threats = [
            Threat360Vector(1, azimuth_deg=0.0, elevation_deg=-45.0, distance_m=100.0, approach_velocity=np.array([-10, 0, -20]))
        ]

        nodes, mode = engine.generate_360_morphing_barrier(threat_vectors=threats, net_mode="AUTO", num_drones=50)
        self.assertEqual(mode, "TOP_COVER_UMBRELLA")

    def test_v_shape_wedge_mesh(self):
        engine = OmnidirectionalBarrierEngine()
        nodes, mode = engine.generate_360_morphing_barrier(threat_vectors=[], net_mode="MULTI_SECTOR_V_SHAPE", num_drones=50)
        self.assertEqual(mode, "MULTI_SECTOR_V_SHAPE")

if __name__ == "__main__":
    unittest.main()
