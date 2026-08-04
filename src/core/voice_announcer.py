import os
import sys
import threading
from typing import Optional

class TacticalVoiceAnnouncer:
    """
    Military Tactical Voice Speaker Announcer (군용 전술 음성 스피커 안내 엔진).
    Provides real-time natural language voice alerts for critical C2 events.
    """
    def __init__(self, enabled: bool = True, language: str = "ko"):
        self.enabled = enabled
        self.language = language
        self.last_announcement: str = ""

    def speak(self, text: str):
        """Announces tactical status over C2 console speaker in background thread."""
        self.last_announcement = text
        if not self.enabled:
            return

        def _say():
            try:
                if sys.platform == "darwin":  # macOS built-in say command
                    voice = "Yuna" if self.language == "ko" else "Alex"
                    os.system(f'say -v "{voice}" "{text}" >/dev/null 2>&1 &')
            except Exception:
                pass

        threading.Thread(target=_say, daemon=True).start()

    def announce_launch(self, drone_count: int = 50):
        self.speak(f"경보 발령. 지상 발사관에서 방어 드론 {drone_count}대 수직 팝업 출격을 개시합니다.")

    def announce_self_healing(self, killed_count: int = 4):
        self.speak(f"적 사격으로 드론 {killed_count}대 피격 파괴. 로컬 에이아이가 0.05초 만에 공중 장막을 자동 복구하였습니다.")

    def announce_interception_success(self):
        self.speak("방어 장막에 침투체 접근 완료. 적 침투체 요격에 성공하였습니다.")

    def announce_scenario_change(self, scenario_name: str):
        if scenario_name == "weaving":
            self.speak("S곡선 회피 기동 침투체 대응 모드로 전환합니다.")
        elif scenario_name == "tilted":
            self.speak("경사 각도 배리어 모드로 전환합니다.")
        elif scenario_name == "saturation":
            self.speak("다수 침투체 포화 공격 대응 모드로 전환합니다.")
        elif scenario_name == "wind":
            self.speak("실시간 돌풍 외란 방어 모드로 전환합니다.")
