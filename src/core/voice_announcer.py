import os
import sys
import threading

class TacticalVoiceAnnouncer:
    """
    Military Tactical Voice Alert Engine (군 전술 음성 안내 엔진).
    Provides concise, objective voice brevity codes.
    """
    def __init__(self, enabled: bool = True, language: str = "ko"):
        self.enabled = enabled
        self.language = language
        self.last_announcement: str = ""

    def speak(self, text: str):
        """Announces concise voice brevity code over speaker."""
        self.last_announcement = text
        if not self.enabled:
            return

        def _say():
            try:
                if sys.platform == "darwin":
                    voice = "Yuna" if self.language == "ko" else "Alex"
                    os.system(f'say -v "{voice}" "{text}" >/dev/null 2>&1 &')
            except Exception:
                pass

        threading.Thread(target=_say, daemon=True).start()

    def announce_launch(self, drone_count: int = 50):
        self.speak(f"팝업 출격 개시. 드론 {drone_count}대 전개.")

    def announce_self_healing(self, killed_count: int = 4):
        self.speak(f"드론 {killed_count}대 피격. 장막 재배치 완료.")

    def announce_interception_success(self):
        self.speak("침투체 요격 완료.")

    def announce_scenario_change(self, scenario_name: str):
        if scenario_name == "weaving":
            self.speak("S곡선 침투 대응 모드.")
        elif scenario_name == "tilted":
            self.speak("경사 배리어 모드.")
        elif scenario_name == "saturation":
            self.speak("포화 공격 대응 모드.")
        elif scenario_name == "wind":
            self.speak("돌풍 외란 방어 모드.")
