import unittest
from src.core.voice_announcer import TacticalVoiceAnnouncer

class TestTacticalVoiceAnnouncer(unittest.TestCase):
    def test_voice_announcer_events(self):
        announcer = TacticalVoiceAnnouncer(enabled=False, language="ko")
        
        announcer.announce_launch(50)
        self.assertIn("팝업 출격", announcer.last_announcement)

        announcer.announce_self_healing(4)
        self.assertIn("장막 재배치 완료", announcer.last_announcement)

        announcer.announce_interception_success()
        self.assertIn("요격 완료", announcer.last_announcement)

if __name__ == "__main__":
    unittest.main()
