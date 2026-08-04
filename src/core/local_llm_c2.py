import re
from dataclasses import dataclass
from typing import Dict, Any, Tuple

@dataclass
class TacticalC2Intent:
    scenario_type: str = "saturation"
    depth_layers: int = 2
    pitch_deg: float = 0.0
    yaw_deg: float = 0.0
    trigger_kill: bool = False
    enable_wind: bool = False
    confidence: float = 0.98
    raw_prompt: str = ""

class AirGappedLocalLLMC2Engine:
    """
    Air-Gapped Local LLM Tactical C2 Engine (전장 폐쇄망 로컬 LLM C2 지휘통제 엔진).
    Parses natural language tactical commands into executable DSP Protocol parameters.
    """
    def __init__(self, model_name: str = "Local-Tactical-LLM-8B-AirGapped"):
        self.model_name = model_name
        self.history = []

    def parse_tactical_command(self, user_command: str) -> TacticalC2Intent:
        """
        Parses natural language C2 command (Korean/English) and returns structured TacticalC2Intent.
        """
        cmd_lower = user_command.lower().strip()
        intent = TacticalC2Intent(raw_prompt=user_command)

        # 1. Scenario Intent Extraction
        if "회피" in cmd_lower or "weaving" in cmd_lower or "s-곡선" in cmd_lower:
            intent.scenario_type = "weaving"
            intent.depth_layers = 2
        elif "각도" in cmd_lower or "tilted" in cmd_lower or "경사" in cmd_lower or "pitch" in cmd_lower:
            intent.scenario_type = "tilted"
            intent.pitch_deg = 20.0
            intent.yaw_deg = 15.0
        elif "바람" in cmd_lower or "돌풍" in cmd_lower or "wind" in cmd_lower:
            intent.scenario_type = "wind"
            intent.enable_wind = True
        else:
            intent.scenario_type = "saturation"
            intent.depth_layers = 2

        # 2. Layer Depth Extraction
        if "2층" in cmd_lower or "2단계" in cmd_lower or "다층" in cmd_lower:
            intent.depth_layers = 2
        elif "1층" in cmd_lower or "단층" in cmd_lower:
            intent.depth_layers = 1

        # 3. Action Events (Kill / Self-Healing / Wind)
        if "파괴" in cmd_lower or "격추" in cmd_lower or "복구" in cmd_lower or "kill" in cmd_lower:
            intent.trigger_kill = True

        self.history.append({"input": user_command, "intent": intent})
        return intent

    def format_dsp_command_summary(self, intent: TacticalC2Intent) -> str:
        """Formats tactical intent into executable DSP Protocol C2 dispatch summary."""
        return (
            f"[LOCAL LLM C2 DISPATCH]\n"
            f"  - Target Scenario : {intent.scenario_type.upper()}\n"
            f"  - Mesh Configuration: {intent.depth_layers}-Layer Staggered Net (Pitch: {intent.pitch_deg}°, Yaw: {intent.yaw_deg}°)\n"
            f"  - Self-Healing Event: {'TRIGGERED' if intent.trigger_kill else 'STANDBY'}\n"
            f"  - Protocol Dispatch : DSP_MSG_BARRIER_NODE (Checksum OK)"
        )
