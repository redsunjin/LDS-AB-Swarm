import unittest
import numpy as np
from src.core.dsp_protocol import DefensiveSwarmProtocol, DSP_MSG_HEARTBEAT, DSP_MSG_APF_THRUST_VECTOR

class TestDSPProtocol(unittest.TestCase):
    def test_encode_decode_heartbeat(self):
        pos = np.array([20.0, 5.0, 30.0])
        vel = np.array([-5.0, 0.0, 1.0])

        pkt = DefensiveSwarmProtocol.encode_heartbeat(
            seq=10, sender_id=5, status=1, battery_mv=16800, pos=pos, vel=vel
        )
        self.assertGreater(len(pkt), 10)

        decoded = DefensiveSwarmProtocol.decode_packet(pkt)
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded["msg_type"], "HEARTBEAT")
        self.assertEqual(decoded["sender_id"], 5)
        self.assertEqual(decoded["status"], 1)
        self.assertEqual(decoded["battery_mv"], 16800)
        np.testing.assert_allclose(decoded["position"], pos, atol=1e-4)

    def test_encode_decode_thrust_vector(self):
        accel = np.array([12.5, -4.2, 8.1])

        pkt = DefensiveSwarmProtocol.encode_thrust_vector(seq=42, sender_id=12, accel=accel)
        decoded = DefensiveSwarmProtocol.decode_packet(pkt)

        self.assertIsNotNone(decoded)
        self.assertEqual(decoded["msg_type"], "THRUST_VECTOR")
        self.assertEqual(decoded["sender_id"], 12)
        np.testing.assert_allclose(decoded["accel"], accel, atol=1e-4)

    def test_invalid_checksum(self):
        accel = np.array([1.0, 2.0, 3.0])
        pkt = bytearray(DefensiveSwarmProtocol.encode_thrust_vector(seq=1, sender_id=1, accel=accel))
        # Corrupt single byte in payload
        pkt[10] ^= 0xFF

        decoded = DefensiveSwarmProtocol.decode_packet(bytes(pkt))
        self.assertIsNone(decoded)

if __name__ == "__main__":
    unittest.main()
