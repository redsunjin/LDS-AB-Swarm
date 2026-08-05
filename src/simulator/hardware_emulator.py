import time
import socket
import threading
import numpy as np
from typing import Dict, List, Optional
from src.core.dsp_protocol import DefensiveSwarmProtocol, DSP_MSG_HEARTBEAT, DSP_MSG_APF_THRUST_VECTOR, DSP_MSG_POPUP_CMD
from src.core.security_engine import DSPSecurityEngine
from src.core.hal_interface import PX4HALAdapter

class VirtualDroneNode:
    """
    Emulates a single physical drone hardware node running DSD-OS HAL & PX4 Autopilot.
    Receives DSP binary control packets over mock socket/stream and executes 6-DoF kinematics.
    """
    def __init__(self, node_id: int, initial_pos: np.ndarray):
        self.node_id = node_id
        self.position = initial_pos.copy()
        self.velocity = np.zeros(3)
        self.battery_mv = 16800  # 4S LiPo voltage (mV)
        self.status = "LANDED"   # LANDED -> POPUP -> BARRIER_ACTIVE -> INTERCEPTED
        self.seq = 0
        self.hal_adapter = PX4HALAdapter(drone_id=node_id, mavlink_sysid=node_id)
        self.security_engine = DSPSecurityEngine()

    def receive_dsp_packet(self, packet_bytes: bytes) -> Optional[bytes]:
        """
        Receives secure DSP binary control packet, decrypts, and executes hardware control loop.
        Returns DSP_MSG_HEARTBEAT telemetry packet.
        """
        decrypted_raw = self.security_engine.decrypt_and_verify(packet_bytes)
        if decrypted_raw is None:
            return None  # Security check failed / Tampered / Replay

        decoded = DefensiveSwarmProtocol.decode_packet(decrypted_raw)
        if decoded is None:
            return None

        # Execute Command Logic
        msg_type = decoded.get("msg_type")
        if msg_type == "THRUST_VECTOR":
            accel = decoded.get("accel", np.zeros(3))
            # Kinematics Update (dt = 0.02s @ 50 Hz loop)
            dt = 0.02
            self.velocity += accel * dt
            self.position += self.velocity * dt
            self.battery_mv = max(14000, self.battery_mv - 1)

        elif msg_type == "RAW":
            self.status = "POPUP"

        # Generate Telemetry Response
        self.seq += 1
        raw_hb = DefensiveSwarmProtocol.encode_heartbeat(
            seq=self.seq, sender_id=self.node_id, status=1 if self.status != "LANDED" else 0,
            battery_mv=self.battery_mv, pos=self.position, vel=self.velocity
        )
        return self.security_engine.encrypt_packet(raw_hb, seq=self.seq, sender_id=self.node_id)


class VirtualHardwareEmulationTestbed:
    """
    End-to-End Hardware Protocol Emulation Testbed (프로토콜 기반 가상 하드웨어 테스트베드).
    Simulates 50 physical drones communicating with C2 via DSP Binary Protocol.
    """
    def __init__(self, num_nodes: int = 50):
        self.nodes: Dict[int, VirtualDroneNode] = {}
        for i in range(1, num_nodes + 1):
            init_pos = np.array([20.0 + (i % 5) * 1.5, (i % 10 - 5) * 2.0, 0.8])
            self.nodes[i] = VirtualDroneNode(node_id=i, initial_pos=init_pos)

    def dispatch_dsp_control_loop(self, control_signals: Dict[int, np.ndarray]) -> Dict[int, Dict]:
        """
        Dispatches DSP control packets to all virtual physical drone nodes and collects telemetry.
        """
        telemetry_map = {}
        for node_id, accel in control_signals.items():
            if node_id in self.nodes:
                node = self.nodes[node_id]
                # 1. Encode DSP Thrust Packet
                raw_pkt = DefensiveSwarmProtocol.encode_thrust_vector(seq=node.seq+1, sender_id=node_id, accel=accel)
                sec_pkt = node.security_engine.encrypt_packet(raw_pkt, seq=node.seq+1, sender_id=node_id)

                # 2. Transmit to Virtual Drone Hardware & Receive Telemetry
                resp_pkt = node.receive_dsp_packet(sec_pkt)
                if resp_pkt:
                    raw_resp = node.security_engine.decrypt_and_verify(resp_pkt)
                    if raw_resp:
                        decoded_hb = DefensiveSwarmProtocol.decode_packet(raw_resp)
                        if decoded_hb:
                            telemetry_map[node_id] = decoded_hb

        return telemetry_map
