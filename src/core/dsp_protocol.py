import struct
import numpy as np
from dataclasses import dataclass
from typing import Tuple, Dict, Any, Optional

# DSP Message Type IDs
DSP_MSG_HEARTBEAT = 0x01
DSP_MSG_UWB_RANGE = 0x02
DSP_MSG_BARRIER_NODE = 0x03
DSP_MSG_APF_THRUST_VECTOR = 0x04
DSP_MSG_POPUP_CMD = 0x05

HEADER_MAGIC = 0x4453  # "DS" in ASCII hex

@dataclass
class DSPMessageHeader:
    magic: int = HEADER_MAGIC
    msg_type: int = 0
    seq: int = 0
    sender_id: int = 0
    payload_len: int = 0

class DefensiveSwarmProtocol:
    """
    Defensive Swarm Protocol (DSP) Open Binary Packet Engine.
    Provides zero-copy struct packing/unpacking over UDP / Serial / MAVLink.
    """
    @staticmethod
    def calc_checksum(data: bytes) -> int:
        """Calculates 16-bit XOR checksum for DSP packet data."""
        checksum = 0xFFFF
        for byte in data:
            checksum ^= byte
        return checksum & 0xFFFF

    @classmethod
    def encode_heartbeat(cls, seq: int, sender_id: int, status: int, battery_mv: int, pos: np.ndarray, vel: np.ndarray) -> bytes:
        """
        Encodes DSP_MSG_HEARTBEAT (0x01) binary packet.
        Payload: status (1B), battery_mv (2B), pos (3x f32), vel (3x f32)
        """
        header = struct.pack(">HHBBH", HEADER_MAGIC, DSP_MSG_HEARTBEAT, seq % 256, sender_id, 27)
        payload = struct.pack(">BHffffff", status, battery_mv, float(pos[0]), float(pos[1]), float(pos[2]), float(vel[0]), float(vel[1]), float(vel[2]))
        raw_pkt = header + payload
        checksum = cls.calc_checksum(raw_pkt)
        return raw_pkt + struct.pack(">H", checksum)

    @classmethod
    def encode_thrust_vector(cls, seq: int, sender_id: int, accel: np.ndarray) -> bytes:
        """
        Encodes DSP_MSG_APF_THRUST_VECTOR (0x04) binary packet.
        Payload: accel_x, accel_y, accel_z (3x f32)
        """
        header = struct.pack(">HHBBH", HEADER_MAGIC, DSP_MSG_APF_THRUST_VECTOR, seq % 256, sender_id, 12)
        payload = struct.pack(">fff", float(accel[0]), float(accel[1]), float(accel[2]))
        raw_pkt = header + payload
        checksum = cls.calc_checksum(raw_pkt)
        return raw_pkt + struct.pack(">H", checksum)

    @classmethod
    def decode_packet(cls, data: bytes) -> Optional[Dict[str, Any]]:
        """
        Decodes any DSP binary packet and validates header magic & checksum.
        """
        if len(data) < 10:
            return None

        magic, msg_type, seq, sender_id, payload_len = struct.unpack(">HHBBH", data[:8])
        if magic != HEADER_MAGIC:
            return None

        total_expected_len = 8 + payload_len + 2
        if len(data) < total_expected_len:
            return None

        pkt_checksum = struct.unpack(">H", data[total_expected_len-2:total_expected_len])[0]
        calculated_checksum = cls.calc_checksum(data[:8 + payload_len])
        if pkt_checksum != calculated_checksum:
            return None  # Checksum mismatch

        payload_bytes = data[8:8 + payload_len]

        if msg_type == DSP_MSG_HEARTBEAT:
            status, battery_mv, px, py, pz, vx, vy, vz = struct.unpack(">BHffffff", payload_bytes)
            return {
                "msg_type": "HEARTBEAT",
                "seq": seq,
                "sender_id": sender_id,
                "status": status,
                "battery_mv": battery_mv,
                "position": np.array([px, py, pz]),
                "velocity": np.array([vx, vy, vz])
            }

        elif msg_type == DSP_MSG_APF_THRUST_VECTOR:
            ax, ay, az = struct.unpack(">fff", payload_bytes)
            return {
                "msg_type": "THRUST_VECTOR",
                "seq": seq,
                "sender_id": sender_id,
                "accel": np.array([ax, ay, az])
            }

        return {"msg_type": "RAW", "sender_id": sender_id, "payload_len": payload_len}
