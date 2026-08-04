# Low-Cost Defensive Swarm Aerial Barrier (LDS-AB)

> **저가형 군집 드론 공중 배리어 요격 시스템 (LDS-AB) 및 C2 지휘통제 관리 콘솔 PoC**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status: Operational PoC](https://img.shields.io/badge/Status-Operational%20PoC-green.svg)]()

---

## 📌 Project Overview (프로젝트 개요)

**LDS-AB (Low-Cost Defensive Swarm Aerial Barrier)** 시스템은 순항 미사일, 회피 기동 자폭 드론 등 저고도 침투 위협을 방어하기 위해 저가형 드론 스웜을 수직 팝업(Pop-Up) 사출시켜 동적 3D 공중 요격 장막을 형성하는 방어 체계입니다.

- **하드웨어 단가 절감**: 개별 드론 카메라는 없으며, 외부 센서 좌표 전달 및 UWB 상대 위치 기반 분산 제어
- **초고속 반응속도**: 로컬 AI 엣지 제어기 연산 지연시간 **< 3.0ms**
- **Self-Healing 복구**: 드론 피격 파괴 시 **0.05초 만에 구멍 난 격자 자동 재배치**
- **GPS-Denied 방해 대응**: 외부 GPS 없이 UWB 상대 거리 메쉬(100 Hz) 기반 형성 유지

---

## 🏗️ System Architecture (시스템 아키텍처)

```
[지상/해상 C2 탐지 레이더] ---> [콜드 가스 공압 팝업 사출 (V >= 20m/s)]
                                        |
                                        v
+-------------------------------------------------------------------+
|  3D Multi-Layer & Multi-Angle Dynamic Barrier Net Mesh            |
|  - Layer 1 (Front Interception) & Layer 2 (Rear Reserve Stagger) |
|  - Pitch / Yaw Dynamic Angle Tilt Orientation                     |
+-------------------------------------------------------------------+
                                        |
                                        v
+-------------------------------------------------------------------+
|  Local AI Edge Swarm Controller (< 3ms Inference)                 |
|  - Decentralized Hungarian Allocation                             |
|  - Artificial Potential Field (APF) & UWB Mesh Repulsion          |
|  - Instantaneous Self-Healing Hole Recovery                       |
+-------------------------------------------------------------------+
```

---

## 🚀 Quick Start (빠른 실행 방법)

### 1. 환경 설정 & 패키지 설치
```bash
git clone https://github.com/redsunjin/LDS-AB-Swarm.git
cd LDS-AB-Swarm

# Virtualenv 설정 및 필수 패키지 설치
uv venv
source .venv/bin/activate
uv pip install numpy scipy matplotlib pytest
```

### 2. C2 운용 관리 콘솔 PoC 실행 (GUI)
```bash
python main_demo.py --scenario saturation
```
- **주요 기능**: 4개 통합 관제 패널 (3D 전장 관제 + 군집 텔레메트리 표 + 적 추적 로그 + C2 시스템 로그)
- **인터랙티브 조종 버튼**: `Scenario A/B/C/D`, `🚀 Relaunch Pop-Up`, `⚡ Kill Drones`, `💨 Wind Gust`

### 3. 3D 웹 인터랙티브 시뮬레이터 실행 (Presentation & Visualizer)
```bash
open visualizer.html
```

### 4. 50회 몬테카를로 물리 정밀도 벤치마크 실행
```bash
python verify_accuracy.py
```

---

## 📊 Benchmark Performance (성능 검증 수치)

50회 몬테카를로(Monte Carlo) 물리 시뮬레이션 벤치마크 검증 결과:

| 검증 항목 (Metric) | 수치 및 성과 (Performance) | 비고 |
| :--- | :--- | :--- |
| **위치 RMS 정밀도** | **$0.815 \text{ m}$** ($\pm 0.227\text{m}$) | 서브미터급 수렴 오차 |
| **Self-Healing 복구 시간** | **$0.050 \text{ s}$** ($50\text{ms}$) | 드론 피격 후 구멍 자동 복구 |
| **Local AI 연산 지연시간** | **$2.831 \text{ ms}$** | 엣지 연산 목표치($< 5.0\text{ms}$) 달성 |
| **UWB 통신 갱신 주파수** | **$100 \text{ Hz}$** | GPS 재밍 환경 무영향 |

---

## 📁 Repository Structure (소스코드 구조)

```text
├── README.md                   # 프로젝트 영문/한글 설명서
├── .gitignore                  # Git 제외 대상 설정
├── main_demo.py                # C2 운용 관리 콘솔 PoC 데모 시나리오 실행기
├── main.py                     # 기본 물리 시뮬레이션 엔트리 포인트
├── mesh_generator.py           # 3D 메시 생성기 루트 모듈
├── verify_accuracy.py          # 50회 몬테카를로 물리 벤치마크 검증 스크립트
├── visualizer.html             # 웹 브라우저 3D 인터랙티브 시뮬레이터 (Presentation용)
├── src/
│   ├── core/
│   │   ├── local_ai_controller.py  # Local AI 엣지 제어기 엔진 (< 3ms)
│   │   ├── mesh_generator.py       # 다층/다층각도 3D 메시 노드 산출기
│   │   ├── swarm_control.py        # APF 및 헝가리안 최적 할당기
│   │   └── geometry.py             # 기초 평면 벡터 산출 모듈
│   ├── simulator/
│   │   ├── drone.py                # 드론 동역학 및 키네마틱 모델
│   │   ├── threat.py               # 침투체 모델 및 예측 궤적
│   │   ├── threat_factory.py       # 다양한 위협 침투체 생성 팩토리
│   │   └── environment.py          # 다중 에이전트 물리 적구 환경 Engine
│   └── visualizer/
│       ├── c2_console.py           # 4개 패널 통합 C2 운용 관리 콘솔 PoC
│       └── plotter.py              # Matplotlib 3D 실시간 관제 플롯
└── tests/                          # 7개 유닛 테스트 모듈
```

---

## 📄 License

This project is licensed under the MIT License.
