import unittest
import numpy as np
from src.core.hva_protection import TacticalAssetProtectionEngine

class TestTacticalAssetProtectionEngine(unittest.TestCase):
    def test_hva_tier_priorities(self):
        engine = TacticalAssetProtectionEngine()
        self.assertEqual(len(engine.hva_list), 3)
        self.assertEqual(engine.hva_list[0].tier, 1)
        self.assertEqual(engine.hva_list[0].priority_weight, 1.0)

    def test_threat_approach_geometry_classification(self):
        engine = TacticalAssetProtectionEngine()
        
        # Steep plunge dive
        geom_steep = engine.classify_threat_approach_geometry(
            threat_pos=np.array([100.0, 0.0, 50.0]),
            threat_vel=np.array([-20.0, 0.0, -15.0])
        )
        self.assertEqual(geom_steep, "STEEP_DIVE_PLUNGING")

        # Valley low corridor
        geom_valley = engine.classify_threat_approach_geometry(
            threat_pos=np.array([100.0, 0.0, 10.0]),
            threat_vel=np.array([-20.0, 0.0, 0.0])
        )
        self.assertEqual(geom_valley, "VALLEY_LOW_CORRIDOR")

    def test_swarm_transit_time_calculation(self):
        engine = TacticalAssetProtectionEngine()
        drone_pos = np.array([25.0, -10.0, 1.0])
        mesh_node = np.array([20.0, 0.0, 25.0])

        transit_time = engine.calculate_swarm_transit_time(drone_pos, mesh_node, max_speed=40.0)
        self.assertGreater(transit_time, 0.0)
        self.assertLess(transit_time, 2.0)

if __name__ == "__main__":
    unittest.main()
