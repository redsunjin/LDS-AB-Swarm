import numpy as np
import time
import argparse
from src.simulator.drone import Drone
from src.simulator.threat import Threat
from src.simulator.environment import SimulationEnvironment
from src.core.mesh_generator import ThreatTrajectory, MeshGenerator
from src.core.swarm_control import SwarmController

def run_simulation(headless: bool = False, max_steps: int = 200):
    print("=" * 65)
    print("  Low-Cost Defensive Swarm Aerial Barrier (LDS-AB) Simulation  ")
    print("=" * 65)

    # 1. Initialize Simulation Environment
    env = SimulationEnvironment(time_step=0.05)

    # 2. Spawn Incoming Threat using ThreatTrajectory (Linear or Curved)
    threat_trajectory = ThreatTrajectory.create_linear(
        start_pos=[160.0, 0.0, 25.0],
        velocity=[-25.0, 0.0, 0.0]
    )
    threat = Threat(
        id=101,
        position=threat_trajectory.get_position(0.0),
        velocity=threat_trajectory.get_velocity(0.0),
        radius=2.5
    )
    env.add_threat(threat)

    # 3. Spawn 25 Swarm Drones from initial ground pop-up positions
    grid_size = (5, 5)
    num_drones = grid_size[0] * grid_size[1]
    
    np.random.seed(42)
    for i in range(num_drones):
        init_pos = np.array([
            np.random.uniform(-10.0, 10.0),
            np.random.uniform(-20.0, 20.0),
            np.random.uniform(2.0, 8.0)
        ])
        drone = Drone(id=i+1, position=init_pos, max_speed=35.0, max_accel=20.0)
        env.add_drone(drone)

    # 4. Initialize Swarm Controller and Mesh Generator
    controller = SwarmController(k_att=3.0, k_rep=18.0, d_rep=7.0, k_damp=1.5)
    mesh_gen = MeshGenerator(default_spacing=8.0)

    # Optional 3D Visualizer
    visualizer = None
    if not headless:
        try:
            from src.visualizer.plotter import SwarmVisualizer
            visualizer = SwarmVisualizer("LDS-AB Dynamic 3D Barrier & Self-Healing PoC")
        except Exception as e:
            print(f"[Warning] Could not initialize GUI visualizer ({e}). Running in headless mode.")
            headless = True

    # 5. Simulation Loop
    target_intercept_time = 4.5  # Seconds ahead for barrier plane
    kill_triggered = False
    self_healing_time = None

    print(f"[Init] Spawned {num_drones} drones and 1 incoming threat at {threat.position}.")
    print("[Loop] Starting physics integration...")

    for step in range(max_steps):
        # Calculate dynamic 3D barrier target nodes using MeshGenerator
        target_nodes = mesh_gen.generate_mesh(
            trajectory=threat_trajectory,
            time_to_intercept=target_intercept_time,
            grid_shape=grid_size
        )

        # Trigger Drone Failure / Destruction event at t=1.5s to test Self-Healing
        if env.current_time >= 1.5 and not kill_triggered:
            print("\n" + "!" * 65)
            print(f"[EVENT] Hostile Countermeasure: Kills 3 Drones (IDs: 3, 7, 12) at t={env.current_time:.2f}s!")
            print("!" * 65 + "\n")
            env.kill_drone(3)
            env.kill_drone(7)
            env.kill_drone(12)
            kill_triggered = True
            kill_time = env.current_time

        # Update Target Allocation (Self-Healing matches remaining drones to nodes)
        controller.solve_target_allocation(env.drones, target_nodes)

        # Calculate Self-Healing Reaction measure
        if kill_triggered and self_healing_time is None:
            # Check if remaining active drones reached new targets
            active_drones = [d for d in env.drones if d.status == "active"]
            distances = [d.distance_to(d.target_position) for d in active_drones if d.target_position is not None]
            if len(distances) > 0 and np.mean(distances) < 2.0:
                self_healing_time = env.current_time - kill_time
                print(f"[SELF-HEALING SUCCESS] Barrier grid restored! Reaction time: {self_healing_time:.3f}s (< 1.0s target)")

        # Compute APF Control Forces
        accel_signals = controller.compute_control_forces(env.drones)

        # Advance Simulation Step
        env.step(accel_signals)

        # Render 3D Frame
        if visualizer and not headless:
            visualizer.render(env.drones, env.threats, target_nodes, env.current_time, grid_size)

        # Check Interception or termination
        if threat.status == "intercepted":
            print(f"\n[SUCCESS] Threat Intercepted at t={env.current_time:.2f}s!")
            break

        time.sleep(0.01 if not headless else 0.0)

    if visualizer and not headless:
        print("\n[Visualizer] Simulation complete! Window remains open for inspection.")
        import matplotlib.pyplot as plt
        plt.show()  # Keep window open until user manually closes it

    print(f"\n[Complete] Simulation ended at t={env.current_time:.2f}s.")
    return env, self_healing_time

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LDS-AB Swarm Barrier Simulation")
    parser.add_argument("--headless", action="store_true", help="Run without Matplotlib 3D window")
    args = parser.parse_args()
    
    run_simulation(headless=args.headless)
