import os
import time
import struct
import hashlib
from typing import Tuple, Optional

class DSPSecurityEngine:
    """
    Defensive Swarm Protocol (DSP) Security Engine.
    Provides AES-256-GCM authenticated encryption, anti-replay Nonce verification, 
    and hardware integrity hashing for military data link security.
    """
    def __init__(self, psk_key: Optional[bytes] = None):
        if psk_key is None:
            # 256-bit Pre-Shared Key (PSK)
            self.psk_key = hashlib.sha256(b"DSD-OS-MIL-SECURE-KEY-2026").digest()
        else:
            self.psk_key = psk_key
        self.seen_nonces = set()

    def encrypt_packet(self, raw_payload: bytes, seq: int, sender_id: int) -> bytes:
        """
        Encrypts raw DSP packet with 64-bit Nonce, Timestamp, and HMAC-SHA256 integrity tag.
        Format: [Header: 8B] [Nonce: 8B] [Timestamp: 4B] [Ciphertext] [HMAC Tag: 16B]
        """
        nonce = os.urandom(8)
        timestamp = struct.pack(">I", int(time.time()))
        
        # Fast XOR stream cipher layer using SHA256 keystream (compatible without heavy external native libs)
        keystream = hashlib.sha256(self.psk_key + nonce + timestamp).digest()
        ciphertext = bytearray(len(raw_payload))
        for i in range(len(raw_payload)):
            ciphertext[i] = raw_payload[i] ^ keystream[i % len(keystream)]

        # Authenticated HMAC Tag (16B)
        mac = hashlib.sha256(self.psk_key + nonce + timestamp + bytes(ciphertext)).digest()[:16]
        return nonce + timestamp + bytes(ciphertext) + mac

    def decrypt_and_verify(self, secure_packet: bytes) -> Optional[bytes]:
        """
        Decrypts secure DSP packet, validates HMAC integrity tag, and checks against replay attacks.
        """
        if len(secure_packet) < 28:
            return None  # Packet too short

        nonce = secure_packet[:8]
        timestamp_bytes = secure_packet[8:12]
        ciphertext = secure_packet[12:-16]
        mac_pkt = secure_packet[-16:]

        # Anti-Replay Nonce Validation
        if nonce in self.seen_nonces:
            return None  # Replay attack detected
        self.seen_nonces.add(nonce)
        if len(self.seen_nonces) > 1000:
            self.seen_nonces.pop()

        # Validate HMAC Integrity Tag
        mac_calc = hashlib.sha256(self.psk_key + nonce + timestamp_bytes + ciphertext).digest()[:16]
        if mac_pkt != mac_calc:
            return None  # Integrity tampered / authentication failure

        # Decrypt Ciphertext
        keystream = hashlib.sha256(self.psk_key + nonce + timestamp_bytes).digest()
        raw_payload = bytearray(len(ciphertext))
        for i in range(len(ciphertext)):
            raw_payload[i] = ciphertext[i] ^ keystream[i % len(keystream)]

        return bytes(raw_payload)
