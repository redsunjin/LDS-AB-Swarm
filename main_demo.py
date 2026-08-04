import numpy as np
import time
import argparse
from src.simulator.drone import Drone
from src.simulator.environment import SimulationEnvironment
from src.core.mesh_generator import MeshGenerator
from src.core.local_ai_controller import LocalAISwarmController
from src.simulator.threat_factory import ThreatFactory

def run_demo_scenario(scenario_type: str = "saturation", headless: bool = False, max_steps: int = 220):
    print("=" * 70)
    print(f"  LDS-AB Multi-Layer & Multi-Angle Swarm Barrier Demo [{scenario_type.upper()}]  ")
    print("=" * 70)

    env = SimulationEnvironment(time_step=0.05)
    mesh_gen = MeshGenerator(default_spacing=7.0)
    ai_controller = LocalAISwarmController(k_att=3.5, k_rep=20.0, d_rep=7.0, k_damp=1.5)

    # 1. Setup Scenario Threats & Barrier Parameters
    depth_layers = 1
    pitch_offset = 0.0
    yaw_offset = 0.0
    grid_shape = (5, 5)

    if scenario_type == "weaving":
        print("[Scenario A] Multi-Layer Staggered Barrier vs S-Curve Weaving Kamikaze Drone")
        threat, trajectory = ThreatFactory.create_weaving_kamikaze(
            threat_id=101, start_pos=(180.0, 0.0, 30.0), speed=28.0, amplitude=12.0
        )
        env.add_threat(threat)
        threat_trajectories = [trajectory]
        depth_layers = 2  # Dual layer barrier
        num_drones = 50

    elif scenario_type == "tilted":
        print("[Scenario B] Multi-Angle Tilted Barrier vs Angled Attack Missile")
        threat, trajectory = ThreatFactory.create_cruise_missile(
            threat_id=101, start_pos=(180.0, 15.0, 20.0), speed=38.0
        )
        env.add_threat(threat)
        threat_trajectories = [trajectory]
        pitch_offset = 20.0  # Tilted pitch
        yaw_offset = 15.0   # Tilted yaw
        num_drones = 25

    else:  # saturation
        print("[Scenario C] Local AI Fast Control vs Multi-Threat Saturation Attack")
        threat_tuples = ThreatFactory.create_saturation_attack()
        threat_trajectories = []
        for t, traj in threat_tuples:
            env.add_threat(t)
            threat_trajectories.append(traj)
        depth_layers = 2
        num_drones = 50

    # 2. Spawn Swarm Drones from Ground Pop-Up Positions
    np.random.seed(42)
    for i in range(num_drones):
        init_pos = np.array([
            np.random.uniform(-12.0, 12.0),
            np.random.uniform(-25.0, 25.0),
            np.random.uniform(2.0, 10.0)
        ])
        drone = Drone(id=i+1, position=init_pos, max_speed=40.0, max_accel=25.0)
        env.add_drone(drone)

    # Optional C2 Console PoC Visualizer
    visualizer = None
    if not headless:
        try:
            from src.visualizer.c2_console import C2ManagementConsolePoC
            visualizer = C2ManagementConsolePoC("LDS-AB OPERATIONAL C2 MANAGEMENT CONSOLE (PoC)")
        except Exception as e:
            print(f"[Warning] C2 GUI visualizer unavailable ({e}). Running in headless mode.")
            headless = True

    # 3. Main Autonomous Defense Simulation Loop
    kill_triggered = False
    target_intercept_time = 4.0

    print(f"[Init] Spawned {num_drones} Swarm Drones and {len(env.threats)} Threats.")
    print("[Loop] Executing Local AI Fast Controller & Multi-Layer Mesh Generation...")

    for step in range(max_steps):
        # Dynamically select lead primary threat trajectory for barrier placement
        lead_traj = threat_trajectories[0]

        # Calculate Multi-Layer, Multi-Angle 3D Grid Nodes
        target_nodes = mesh_gen.generate_mesh(
            trajectory=lead_traj,
            time_to_intercept=target_intercept_time,
            grid_shape=grid_shape,
            depth_layers=depth_layers,
            layer_stagger=True,
            pitch_offset_deg=pitch_offset,
            yaw_offset_deg=yaw_offset
        )

        # Trigger Countermeasure Destruction at t=2.0s to test Self-Healing
        if env.current_time >= 2.0 and not kill_triggered:
            print("\n" + "!" * 70)
            print(f"[EVENT] Hostile Countermeasure: Kills 4 Drones at t={env.current_time:.2f}s!")
            print("!" * 70 + "\n")
            env.kill_drone(5)
            env.kill_drone(10)
            env.kill_drone(15)
            env.kill_drone(20)
            kill_triggered = True

        # Local AI Edge Controller Execution (< 5ms response)
        accel_signals, ai_latency_ms = ai_controller.compute_control_signals(env.drones, target_nodes)

        # Physics Step
        env.step(accel_signals)

        # Render C2 Management Console PoC GUI
        if visualizer and not headless:
            visualizer.render_console(env.drones, env.threats, target_nodes, env.current_time, 
                                       grid_shape=grid_shape, depth_layers=depth_layers, 
                                       local_ai_latency_ms=ai_latency_ms)

        # Check Interceptions
        intercepted_count = sum(1 for t in env.threats if t.status == "intercepted")
        if intercepted_count == len(env.threats):
            print(f"\n[SUCCESS] ALL {intercepted_count} Threats Intercepted by Swarm Barrier at t={env.current_time:.2f}s!")
            break

        time.sleep(0.01 if not headless else 0.0)

    if visualizer and not headless:
        print("\n[Visualizer] Simulation complete! Window remains open for inspection.")
        print("  - Use left-click drag to rotate 3D view")
        print("  - Use right-click drag or zoom tool to zoom in/out")
        import matplotlib.pyplot as plt
        plt.show()  # Keep window open until user manually closes it

    print(f"[Complete] Scenario '{scenario_type}' finished at t={env.current_time:.2f}s (Avg AI Latency: {ai_controller.last_inference_time_ms:.2f}ms).")
    return env

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LDS-AB Automated Multi-Threat Swarm Defense Demo")
    parser.add_argument("--scenario", type=str, default="saturation", choices=["weaving", "tilted", "saturation"], 
                        help="Select scenario: weaving, tilted, or saturation")
    parser.add_argument("--headless", action="store_true", help="Run without Matplotlib GUI window")
    args = parser.parse_args()

    run_demo_scenario(scenario_type=args.scenario, headless=args.headless)
