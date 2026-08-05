import unittest
from src.core.security_engine import DSPSecurityEngine
from src.core.dsp_protocol import DefensiveSwarmProtocol
import numpy as np

class TestDSPSecurityEngine(unittest.TestCase):
    def test_encrypt_decrypt_integrity(self):
        engine = DSPSecurityEngine()
        raw_pkt = DefensiveSwarmProtocol.encode_heartbeat(
            seq=1, sender_id=5, status=1, battery_mv=16800,
            pos=np.array([10.0, 0.0, 5.0]), vel=np.array([0.0, 0.0, 0.0])
        )

        sec_pkt = engine.encrypt_packet(raw_pkt, seq=1, sender_id=5)
        self.assertGreater(len(sec_pkt), len(raw_pkt))

        decrypted = engine.decrypt_and_verify(sec_pkt)
        self.assertIsNotNone(decrypted)
        self.assertEqual(decrypted, raw_pkt)

    def test_tampered_packet_rejection(self):
        engine = DSPSecurityEngine()
        raw_pkt = b"TEST_DSP_PACKET_DATA"
        sec_pkt = bytearray(engine.encrypt_packet(raw_pkt, seq=1, sender_id=5))

        # Corrupt single byte
        sec_pkt[15] ^= 0xFF

        decrypted = engine.decrypt_and_verify(bytes(sec_pkt))
        self.assertIsNone(decrypted)

    def test_anti_replay_rejection(self):
        engine = DSPSecurityEngine()
        raw_pkt = b"TEST_DSP_PACKET_DATA"
        sec_pkt = engine.encrypt_packet(raw_pkt, seq=1, sender_id=5)

        # First decryption OK
        dec1 = engine.decrypt_and_verify(sec_pkt)
        self.assertIsNotNone(dec1)

        # Replay same packet fails
        dec2 = engine.decrypt_and_verify(sec_pkt)
        self.assertIsNone(dec2)

if __name__ == "__main__":
    unittest.main()
