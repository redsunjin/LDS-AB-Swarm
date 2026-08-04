import unittest
from src.core.local_llm_c2 import AirGappedLocalLLMC2Engine

class TestAirGappedLocalLLMC2(unittest.TestCase):
    def test_parse_weaving_command(self):
        engine = AirGappedLocalLLMC2Engine()
        intent = engine.parse_tactical_command("S-곡선 회피 침투 드론 진입, 2층 배리어 전개해")

        self.assertEqual(intent.scenario_type, "weaving")
        self.assertEqual(intent.depth_layers, 2)

    def test_parse_tilted_command(self):
        engine = AirGappedLocalLLMC2Engine()
        intent = engine.parse_tactical_command("20도 경사 각도 배리어로 전개하고 파괴 드론 복구해")

        self.assertEqual(intent.scenario_type, "tilted")
        self.assertEqual(intent.pitch_deg, 20.0)
        self.assertTrue(intent.trigger_kill)

    def test_parse_wind_command(self):
        engine = AirGappedLocalLLMC2Engine()
        intent = engine.parse_tactical_command("돌풍 바람 외란 환경 반영해")

        self.assertEqual(intent.scenario_type, "wind")
        self.assertTrue(intent.enable_wind)

if __name__ == "__main__":
    unittest.main()
