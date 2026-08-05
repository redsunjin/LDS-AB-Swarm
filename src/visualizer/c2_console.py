import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.gridspec as gridspec
from matplotlib.widgets import Button, TextBox
import numpy as np
from typing import List, Tuple, Optional, Callable
from src.simulator.drone import Drone
from src.simulator.threat import Threat
from src.core.local_llm_c2 import AirGappedLocalLLMC2Engine, TacticalC2Intent
from src.core.dsp_protocol import DefensiveSwarmProtocol
from src.core.voice_announcer import TacticalVoiceAnnouncer

class C2ManagementConsolePoC:
    """
    DSD-OS Military Operational C2 Touchscreen Console PoC.
    HMI Architecture:
      - Primary Control: Ruggedized Touchscreen Buttons (Deterministic Mechanical Execution)
      - Auxiliary Feedback: Real-Time Tactical Natural Language Voice Speaker Announcements
      - Auxiliary Input: Secondary Speech/Prompt Assistant
    """
    def __init__(self, title: str = "DSD-OS MILITARY TOUCHSCREEN C2 CONSOLE (PoC)"):
        plt.style.use('dark_background')
        self.fig = plt.figure(figsize=(16, 9.5), facecolor='#0b0f19')
        self.fig.canvas.manager.set_window_title("DSD-OS Tactical C2 Management Console v1.0")

        # Load brand icon if supported by GUI backend
        try:
            import matplotlib.image as mpimg
            icon_img = mpimg.imread('assets/favicon.png')
            if hasattr(self.fig.canvas.manager, 'window') and hasattr(self.fig.canvas.manager.window, 'iconphoto'):
                self.fig.canvas.manager.window.iconphoto(False, icon_img)
        except Exception:
            pass

        self.voice_announcer = TacticalVoiceAnnouncer(enabled=True, language="ko")
        self.llm_engine = AirGappedLocalLLMC2Engine()

        # Layout: 13x16 GridSpec
        gs = gridspec.GridSpec(13, 16, figure=self.fig)

        # 1. Main 3D Airspace Panel (Left side: rows 0-12, cols 0-10)
        self.ax_3d = self.fig.add_subplot(gs[0:13, 0:10], projection='3d')
        self.ax_3d.set_facecolor('#0f172a')

        # 2. Swarm Telemetry Panel (Top right: rows 0-3, cols 10-16)
        self.ax_telemetry = self.fig.add_subplot(gs[0:3, 10:16])
        self.ax_telemetry.set_facecolor('#0f172a')
        self.ax_telemetry.axis('off')

        # 3. Threat Tracking Panel (Middle right: rows 3-5, cols 10-16)
        self.ax_threat = self.fig.add_subplot(gs[3:5, 10:16])
        self.ax_threat.set_facecolor('#0f172a')
        self.ax_threat.axis('off')

        # 4. System Logs & Voice Status Panel (Middle-lower right: rows 5-8, cols 10-16)
        self.ax_log = self.fig.add_subplot(gs[5:8, 10:16])
        self.ax_log.set_facecolor('#0f172a')
        self.ax_log.axis('off')

        # Controls Background
        self.ax_cmd_bg = self.fig.add_subplot(gs[8:13, 10:16])
        self.ax_cmd_bg.set_facecolor('#0f172a')
        self.ax_cmd_bg.axis('off')

        self.last_log_messages: List[str] = [
            "DSD-OS Military Touchscreen Console Ready.",
            "Primary Control: Ruggedized Touchscreen UI Active.",
            "Auxiliary Voice Announcer: ONLINE (Speaker Active).",
            "DSP Binary Protocol Engine: 100 Hz Streaming."
        ]

        # Callbacks
        self.on_scenario_change: Optional[Callable[[str], None]] = None
        self.on_kill_drones: Optional[Callable[[], None]] = None
        self.on_relaunch: Optional[Callable[[], None]] = None

        self._setup_touchscreen_controls(gs)

    def _setup_touchscreen_controls(self, gs):
        """Build Ruggedized Touchscreen Control Panel."""
        # Row 1: Deterministic Touchscreen Action Buttons
        ax_btn_launch = self.fig.add_subplot(gs[8, 10:13])
        ax_btn_kill = self.fig.add_subplot(gs[8, 13:16])
        self.btn_launch = Button(ax_btn_launch, '🚀 POP-UP LAUNCH (사출)', color='#2563eb', hovercolor='#1d4ed8')
        self.btn_kill = Button(ax_btn_kill, '⚡ COUNTERMEASURE (피격)', color='#dc2626', hovercolor='#b91c1c')

        # Row 2: Touchscreen Mode Selectors
        ax_btn_mode_a = self.fig.add_subplot(gs[9, 10:13])
        ax_btn_mode_b = self.fig.add_subplot(gs[9, 13:16])
        self.btn_mode_a = Button(ax_btn_mode_a, 'MODE: S-Weaving (회피)', color='#1e293b', hovercolor='#0284c7')
        self.btn_mode_b = Button(ax_btn_mode_b, 'MODE: Tilted Net (경사)', color='#1e293b', hovercolor='#0284c7')

        ax_btn_mode_c = self.fig.add_subplot(gs[10, 10:13])
        ax_btn_mode_d = self.fig.add_subplot(gs[10, 13:16])
        self.btn_mode_c = Button(ax_btn_mode_c, 'MODE: Saturation (포화)', color='#0284c7', hovercolor='#0f766e')
        self.btn_mode_d = Button(ax_btn_mode_d, 'MODE: Wind Gust (돌풍)', color='#1e293b', hovercolor='#d97706')

        # Row 3: Voice Guidance Toggle & Secondary Input Box
        ax_btn_voice = self.fig.add_subplot(gs[11, 10:13])
        ax_txt_speech = self.fig.add_subplot(gs[11, 13:16])
        self.btn_voice = Button(ax_btn_voice, '🔊 VOICE SPEAKER: ON', color='#059669', hovercolor='#047857')
        self.txt_speech = TextBox(ax_txt_speech, 'Voice Prompt: ', initial='보조 음성 명령', color='#1e293b', hovercolor='#0284c7')

        # Event Bindings
        self.btn_launch.on_clicked(lambda e: self._trigger_relaunch())
        self.btn_kill.on_clicked(lambda e: self._trigger_kill())

        self.btn_mode_a.on_clicked(lambda e: self._change_mode("weaving"))
        self.btn_mode_b.on_clicked(lambda e: self._change_mode("tilted"))
        self.btn_mode_c.on_clicked(lambda e: self._change_mode("saturation"))
        self.btn_mode_d.on_clicked(lambda e: self._change_mode("wind"))

        self.btn_voice.on_clicked(self._toggle_voice)
        self.txt_speech.on_submit(self._on_speech_input)

    def _toggle_voice(self, event):
        self.voice_announcer.enabled = not self.voice_announcer.enabled
        state_str = "ON" if self.voice_announcer.enabled else "OFF"
        color_str = "#059669" if self.voice_announcer.enabled else "#475569"
        self.btn_voice.label.set_text(f"🔊 VOICE SPEAKER: {state_str}")
        self.btn_voice.color = color_str
        self.log(f"[C2 Voice] Tactical Speaker Guidance: {state_str}")
        if self.voice_announcer.enabled:
            self.voice_announcer.speak("전술 음성 스피커 안내 시스템이 활성화되었습니다.")

    def _change_mode(self, mode_name: str):
        self.log(f"[TOUCHSCREEN] Mode Switched to '{mode_name.upper()}'")
        self.voice_announcer.announce_scenario_change(mode_name)
        if self.on_scenario_change:
            self.on_scenario_change(mode_name)

    def _trigger_relaunch(self):
        self.log("[TOUCHSCREEN] Deterministic Action: Pop-Up Launch Triggered!")
        self.voice_announcer.announce_launch(50)
        if self.on_relaunch:
            self.on_relaunch()

    def _trigger_kill(self):
        self.log("[TOUCHSCREEN] Deterministic Action: Countermeasure Executed!")
        self.voice_announcer.announce_self_healing(4)
        if self.on_kill_drones:
            self.on_kill_drones()

    def _on_speech_input(self, text: str):
        intent = self.llm_engine.parse_tactical_command(text)
        self.log(f"[Aux Voice Input] '{text}' -> {intent.scenario_type.upper()}")
        self._change_mode(intent.scenario_type)

    def log(self, msg: str):
        self.last_log_messages.append(msg)
        if len(self.last_log_messages) > 5:
            self.last_log_messages.pop(0)

    def render_console(self, 
                       drones: List[Drone], 
                       threats: List[Threat], 
                       target_nodes: np.ndarray, 
                       sim_time: float, 
                       grid_shape: Tuple[int, int] = (5, 5),
                       depth_layers: int = 2,
                       local_ai_latency_ms: float = 2.82):
        """Renders complete DSD-OS Touchscreen C2 Management Console."""
        # 1. 3D Airspace Panel
        self.ax_3d.cla()
        self.ax_3d.set_title(f"DSD-OS 3D AIRSPACE TRACKING | T = {sim_time:.2f}s", color='#00ffcc', fontsize=11, fontweight='bold')
        self.ax_3d.set_xlabel('X: Distance to Base (m)', color='#94a3b8', fontsize=8)
        self.ax_3d.set_ylabel('Y: Width (m)', color='#94a3b8', fontsize=8)
        self.ax_3d.set_zlabel('Z: Altitude (m)', color='#94a3b8', fontsize=8)
        self.ax_3d.grid(True, linestyle='--', alpha=0.25)
        self.ax_3d.view_init(elev=22, azim=135)

        self.ax_3d.plot([20, 20], [-20, 20], [0, 0], color='#00ffcc', linestyle='-', linewidth=2.5, alpha=0.7, label='Base Anchor (X=20m)')

        if target_nodes is not None and len(target_nodes) > 0:
            nodes_arr = np.array(target_nodes)
            rows, cols = grid_shape
            nodes_per_layer = rows * cols

            for l in range(depth_layers):
                start_idx = l * nodes_per_layer
                end_idx = (l + 1) * nodes_per_layer
                if end_idx <= len(nodes_arr):
                    layer_nodes = nodes_arr[start_idx:end_idx]
                    grid_matrix = layer_nodes.reshape((rows, cols, 3))
                    color_code = '#00ffcc' if l == 0 else '#ffd700'
                    self.ax_3d.scatter(layer_nodes[:, 0], layer_nodes[:, 1], layer_nodes[:, 2], color=color_code, s=16, alpha=0.6)

                    for r in range(rows):
                        self.ax_3d.plot(grid_matrix[r, :, 0], grid_matrix[r, :, 1], grid_matrix[r, :, 2], color=color_code, linestyle=':', alpha=0.35)
                    for c in range(cols):
                        self.ax_3d.plot(grid_matrix[:, c, 0], grid_matrix[:, c, 1], grid_matrix[:, c, 2], color=color_code, linestyle=':', alpha=0.35)

        active_drones = [d for d in drones if d.status == "active"]
        destroyed_drones = [d for d in drones if d.status in ("destroyed", "intercepted")]

        if active_drones:
            act_pos = np.array([d.position for d in active_drones])
            self.ax_3d.scatter(act_pos[:, 0], act_pos[:, 1], act_pos[:, 2], color='#4ade80', s=45, depthshade=True, label=f'Active ({len(active_drones)})')

        if destroyed_drones:
            des_pos = np.array([d.position for d in destroyed_drones])
            self.ax_3d.scatter(des_pos[:, 0], des_pos[:, 1], des_pos[:, 2], color='#ef4444', marker='x', s=75, label=f'Destroyed ({len(destroyed_drones)})')

        for t in threats:
            t_color = '#ff3333' if t.status == "approaching" else 'orange'
            self.ax_3d.scatter(t.position[0], t.position[1], t.position[2], color=t_color, s=90)
            vel_norm = np.linalg.norm(t.velocity)
            if vel_norm > 1e-3:
                v_dir = t.velocity / vel_norm
                self.ax_3d.quiver(t.position[0], t.position[1], t.position[2],
                                  v_dir[0]*20, v_dir[1]*20, v_dir[2]*20, color='#ff3333', linewidth=2.5, arrow_length_ratio=0.3)

        self.ax_3d.set_xlim(200, -20)
        self.ax_3d.set_ylim(-35, 35)
        self.ax_3d.set_zlim(0, 60)
        self.ax_3d.legend(loc='upper left', facecolor='#0b0f19', edgecolor='#00ffcc', fontsize=8)

        # 2. Telemetry Panel
        self.ax_telemetry.cla()
        self.ax_telemetry.axis('off')
        self.ax_telemetry.set_title("SWARM TELEMETRY & OPEN HAL STATUS", color='#38bdf8', fontsize=9.5, fontweight='bold', loc='left')

        table_text = "DRONE ID   HAL PLATFORM           STATUS     SPEED      DSP STREAM\n"
        table_text += "-" * 58 + "\n"
        for d in drones[:4]:
            status_str = "ACTIVE  " if d.status == "active" else "DESTROY "
            speed = np.linalg.norm(d.velocity)
            table_text += f"ID-{d.id:02d}     PX4_MAVLINK/SIM        {status_str}   {speed:4.1f}m/s    0x01 (100Hz)\n"
        table_text += f"... Total Monitored: {len(drones)} (Active: {len(active_drones)}, Dead: {len(destroyed_drones)})\n"
        self.ax_telemetry.text(0.02, 0.90, table_text, family='monospace', fontsize=7.2, color='#e2e8f0', verticalalignment='top')

        # 3. Threat Tracking Panel
        self.ax_threat.cla()
        self.ax_threat.axis('off')
        self.ax_threat.set_title("THREAT TARGET TRACKING & ENGAGEMENT", color='#ff3333', fontsize=9.5, fontweight='bold', loc='left')

        threat_info = ""
        for t in threats:
            dist_to_base = abs(t.position[0] - 20.0)
            threat_info += f"TARGET #{t.id} [{t.status.upper()}]  |  Range: {dist_to_base:.1f} m  |  Vel: {np.linalg.norm(t.velocity):.1f} m/s\n"
        self.ax_threat.text(0.02, 0.90, threat_info, family='monospace', fontsize=7.5, color='#fca5a5', verticalalignment='top')

        # 4. Logs & Voice Status Panel
        self.ax_log.cla()
        self.ax_log.axis('off')
        self.ax_log.set_title("MILITARY HMI LOGS & TACTICAL VOICE SPEAKER STATUS", color='#facc15', fontsize=9.5, fontweight='bold', loc='left')

        log_text = f"Primary Control: Touchscreen UI | Auxiliary Feedback: Tactical Voice Speaker ({'ACTIVE' if self.voice_announcer.enabled else 'DISABLED'})\n"
        log_text += f"Last Speaker Voice Output: \"{self.voice_announcer.last_announcement}\"\n"
        log_text += "-" * 58 + "\n"
        for l in self.last_log_messages:
            log_text += f"> {l}\n"
        self.ax_log.text(0.02, 0.90, log_text, family='monospace', fontsize=7.2, color='#fef08a', verticalalignment='top')

        plt.draw()
        plt.pause(0.001)
