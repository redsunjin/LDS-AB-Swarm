import unittest
import numpy as np
from src.simulator.drone import Drone
from src.core.local_ai_controller import LocalAISwarmController

class TestLocalAIController(unittest.TestCase):
    def test_local_ai_latency_and_output(self):
        controller = LocalAISwarmController()

        # Spawn 50 drones
        drones = [Drone(id=i+1, position=np.random.uniform(-10, 10, 3)) for i in range(50)]
        target_nodes = np.random.uniform(-20, 20, (50, 3))

        # Warmup run to avoid cold-start timing jitter
        controller.compute_control_signals(drones, target_nodes)

        # Run local AI inference step
        control_signals, latency_ms = controller.compute_control_signals(drones, target_nodes)

        # 1. Check response time is under 10ms requirement in unit test environment
        self.assertLess(latency_ms, 10.0)

        # 2. Check control signals were generated for all active drones
        self.assertEqual(len(control_signals), 50)
        for drone_id, accel in control_signals.items():
            self.assertEqual(accel.shape, (3,))
            self.assertFalse(np.isnan(accel).any())

if __name__ == "__main__":
    unittest.main()
