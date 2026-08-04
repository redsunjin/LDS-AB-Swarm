# DSD-OS: Defensive Swarm Drone Operating System

> **오픈 디바이스 및 호환 프로토콜(DSP) 기반 저가형 방어 드론 전용 운용 OS (Defensive Swarm OS)**
> **하드웨어 종속 탈피 (Hardware-Agnostic) + 군용 폐쇄망 로컬 LLM C2 솔루션**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: Proprietary Commercial](https://img.shields.io/badge/License-Proprietary%20%2F%20Commercial-red.svg)](LICENSE)
[![Architecture: DSD--OS v1.0](https://img.shields.io/badge/Architecture-DSD--OS%20v1.0-cyan.svg)]()

---

## 🎯 1. Project Strategic Vision (프로젝트 전략 비전)

**DSD-OS (Defensive Swarm Drone Operating System)**는 특정 드론 기체나 발사대 하드웨어에 종속되지 않고, 소프트웨어 중심의 오픈 디바이스 지원을 지향하는 **방어 드론 전용 운용 OS (Software-Defined Swarm Defense OS)**입니다.

- **오픈 디바이스 & 표준 호환 프로토콜 (DSP)**: PX4, ArduPilot, ROS 2, 자작 FPV, 방산 군용 드론 등 모든 기종과 연동되는 **Defensive Swarm Protocol (DSP)** 정의
- **군사 보안 폐쇄망 로컬 LLM C2 통합**: 외부 클라우드 연결 없이 온프레미스 장비에서 구동되는 **Local Edge LLM 기반 자연어 전장 판단 및 C2 지휘통제**
- **군용 턴키 솔루션 납품 모델 (Mil-Spec Solution)**: 구독형 모델을 배제하고 방산 체계업체 및 군에 온프레미스 솔루션으로 납품되는 방방어 무기체계 소프트웨어

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

## 📄 License & Copyright (라이선스 및 저작권)

**Copyright (c) 2026 redsunjin. All Rights Reserved. (상업용 / 독점 라이선스)**

본 프로젝트의 모든 소스코드, 3D 시뮬레이터, C2 콘솔 PoC, 알고리즘 및 문서 자산은 **redsunjin**의 독점 자산 및 상업용 지적 재산입니다. 저작권자의 사전 서면 동의 없는 무단 복제, 배포, 수정, 무단 도용 및 상업적 이용을 엄격히 금지합니다.

