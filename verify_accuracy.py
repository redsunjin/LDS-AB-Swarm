import numpy as np
import time
from typing import Dict, List, Tuple
from src.simulator.drone import Drone
from src.simulator.environment import SimulationEnvironment
from src.core.mesh_generator import MeshGenerator
from src.core.local_ai_controller import LocalAISwarmController
from src.simulator.threat_factory import ThreatFactory

class AccuracyVerificationBenchmark:
    """
    Monte Carlo Physics Simulation Benchmark for evaluating:
    1. Interception Rate (Direct Hit vs Fragment Proximity vs Miss)
    2. Positioning RMS Accuracy (meters) under sensor noise & wind disturbance
    3. Self-Healing Grid Recovery Time (seconds)
    4. Local AI Control Loop Speed (milliseconds)
    """
    def __init__(self, num_trials: int = 50, sensor_noise_std: float = 0.15):
        self.num_trials = num_trials
        self.sensor_noise_std = sensor_noise_std
        self.results = {
            "direct_hits": 0,
            "fragment_hits": 0,
            "misses": 0,
            "position_errors_m": [],
            "self_healing_times_s": [],
            "ai_latencies_ms": []
        }

    def run_single_trial(self, trial_id: int, threat_type: str = "weaving") -> Dict:
        env = SimulationEnvironment(time_step=0.05)
        mesh_gen = MeshGenerator(default_spacing=6.5)
        ai_controller = LocalAISwarmController(k_att=3.5, k_rep=20.0, d_rep=6.5, k_damp=1.5)

        # 1. Create Threat & Trajectory
        if threat_type == "weaving":
            threat, trajectory = ThreatFactory.create_weaving_kamikaze(
                threat_id=200 + trial_id, start_pos=(170.0, 0.0, 30.0), speed=32.0, amplitude=10.0
            )
        elif threat_type == "missile":
            threat, trajectory = ThreatFactory.create_cruise_missile(
                threat_id=200 + trial_id, start_pos=(170.0, 10.0, 25.0), speed=42.0
            )
        else:
            threat, trajectory = ThreatFactory.create_weaving_kamikaze(
                threat_id=200 + trial_id, start_pos=(170.0, -10.0, 20.0), speed=30.0, amplitude=8.0
            )

        env.add_threat(threat)

        # 2. Spawn 50 Drones with pre-allocation around Defense Station (X=20m)
        num_drones = 50
        grid_shape = (5, 5)
        depth_layers = 2

        np.random.seed(trial_id * 100 + 7)
        for i in range(num_drones):
            init_pos = np.array([
                np.random.uniform(18.0, 22.0),
                np.random.uniform(-10.0, 10.0),
                np.random.uniform(15.0, 35.0)
            ])
            drone = Drone(id=i+1, position=init_pos, max_speed=45.0, max_accel=35.0)
            env.add_drone(drone)

        # 3. Physics Simulation Integration
        kill_triggered = False
        kill_time = None
        healing_time = None
        trial_errors = []
        trial_latencies = []
        final_interception_type = "miss"

        for step in range(250):  # max 12.5 seconds
            # Anchor Defensive Aerial Net at fixed intercept corridor (X=20m, Y=0m, Z=25m)
            rows, cols = grid_shape
            nodes = []
            for layer in range(depth_layers):
                depth_offset = (layer - (depth_layers - 1) / 2.0) * 4.0
                layer_center = np.array([20.0 + depth_offset, 0.0, 25.0])
                stagger_z = 2.0 if (layer % 2 == 1) else 0.0
                for r in range(rows):
                    for c in range(cols):
                        node_pos = layer_center + np.array([0.0, (r - 2) * 4.0, (c - 2) * 4.0 + stagger_z])
                        nodes.append(node_pos)
            target_nodes = np.array(nodes)

            # Proportional Navigation (PN) Terminal Guidance: When threat is within 35m, lock on to threat position
            if threat.position[0] <= 35.0:
                active_drones = [d for d in env.drones if d.status == "active"]
                for d in active_drones:
                    dist_to_t = np.linalg.norm(d.position - threat.position)
                    if dist_to_t < 25.0:
                        # Terminal pursuit vector towards predicted threat position
                        lead_threat_pos = threat.position + threat.velocity * (dist_to_t / 45.0)
                        d.target_position = lead_threat_pos

            # Inject Realistic UWB Sensor Ranging Noise & Wind Gusts
            noise = np.random.normal(0.0, self.sensor_noise_std, size=target_nodes.shape)
            noisy_target_nodes = target_nodes + noise

            # Trigger Countermeasure Drone Destruction at t=1.8s
            if env.current_time >= 1.8 and not kill_triggered:
                kill_ids = np.random.choice([d.id for d in env.drones if d.status == "active"], size=3, replace=False)
                for k_id in kill_ids:
                    env.kill_drone(k_id)
                kill_triggered = True
                kill_time = env.current_time

            # Compute Local AI Control Signals
            accel_signals, ai_lat_ms = ai_controller.compute_control_signals(env.drones, noisy_target_nodes)
            trial_latencies.append(ai_lat_ms)

            # Apply Wind Disturbance Force to Active Drones
            wind_force = np.random.uniform(-1.5, 1.5, size=3)
            for d_id in accel_signals:
                accel_signals[d_id] += wind_force

            # Step Physics
            env.step(accel_signals)

            # Track Positioning RMS Accuracy
            active_drones = [d for d in env.drones if d.status == "active" and d.target_position is not None]
            if active_drones:
                errs = [np.linalg.norm(d.position - d.target_position) for d in active_drones]
                trial_errors.append(np.mean(errs))

                # Track Self-Healing Recovery Time
                if kill_triggered and healing_time is None:
                    if np.mean(errs) < 2.0:
                        healing_time = env.current_time - kill_time

            # Interception Collision Distance Analysis (Continuous Segment Check)
            prev_threat_pos = threat.position - threat.velocity * env.dt
            threat_pos = threat.position

            min_dist_to_threat = 999.0
            for d in env.drones:
                if d.status != "active":
                    continue
                # Distance from drone position to line segment [prev_threat_pos, threat_pos]
                seg = threat_pos - prev_threat_pos
                seg_len_sq = np.dot(seg, seg)
                if seg_len_sq < 1e-6:
                    dist = d.distance_to(threat_pos)
                else:
                    t_proj = max(0.0, min(1.0, np.dot(d.position - prev_threat_pos, seg) / seg_len_sq))
                    closest_pt = prev_threat_pos + t_proj * seg
                    dist = np.linalg.norm(d.position - closest_pt)

                if dist < min_dist_to_threat:
                    min_dist_to_threat = dist

            if min_dist_to_threat <= 0.8:
                final_interception_type = "direct_hit"
                threat.status = "intercepted"
                break
            elif min_dist_to_threat <= 2.5:
                final_interception_type = "fragment_hit"
                threat.status = "intercepted"
                break

            if threat.position[0] < -10.0:
                final_interception_type = "miss"
                break

        return {
            "trial_id": trial_id,
            "result": final_interception_type,
            "avg_error_m": np.mean(trial_errors) if trial_errors else 0.0,
            "healing_time_s": healing_time if healing_time is not None else 0.0,
            "avg_ai_latency_ms": np.mean(trial_latencies) if trial_latencies else 0.0
        }

    def execute_benchmark(self) -> Dict:
        print("=" * 75)
        print(f"  LDS-AB Monte Carlo Physics Verification Benchmark ({self.num_trials} Trials)  ")
        print("=" * 75)
        print(f"[Config] UWB Sensor Ranging Noise: +/-{self.sensor_noise_std * 100:.1f} cm | Wind Gusts Enabled")
        print("[Loop] Running Monte Carlo physics trials...\n")

        start_bench = time.time()
        for i in range(self.num_trials):
            threat_type = ["weaving", "missile"][i % 2]
            res = self.run_single_trial(trial_id=i+1, threat_type=threat_type)

            if res["result"] == "direct_hit":
                self.results["direct_hits"] += 1
            elif res["result"] == "fragment_hit":
                self.results["fragment_hits"] += 1
            else:
                self.results["misses"] += 1

            self.results["position_errors_m"].append(res["avg_error_m"])
            if res["healing_time_s"] > 0:
                self.results["self_healing_times_s"].append(res["healing_time_s"])
            self.results["ai_latencies_ms"].append(res["avg_ai_latency_ms"])

            if (i + 1) % 10 == 0 or (i + 1) == self.num_trials:
                print(f"  Progress: [{i+1:2d}/{self.num_trials}] | Direct Hits: {self.results['direct_hits']} | Fragment Hits: {self.results['fragment_hits']} | Misses: {self.results['misses']}")

        total_bench_time = time.time() - start_bench
        
        # Summary Calculations
        total_interceptions = self.results["direct_hits"] + self.results["fragment_hits"]
        success_rate = (total_interceptions / self.num_trials) * 100.0
        direct_hit_rate = (self.results["direct_hits"] / self.num_trials) * 100.0
        fragment_hit_rate = (self.results["fragment_hits"] / self.num_trials) * 100.0
        mean_pos_error = np.mean(self.results["position_errors_m"])
        std_pos_error = np.std(self.results["position_errors_m"])
        mean_healing = np.mean(self.results["self_healing_times_s"]) if self.results["self_healing_times_s"] else 0.0
        mean_ai_lat = np.mean(self.results["ai_latencies_ms"])

        print("\n" + "=" * 75)
        print("  FINAL ACCURACY VERIFICATION BENCHMARK SUMMARY  ")
        print("=" * 75)
        print(f" Total Trials Run             : {self.num_trials}")
        print(f" Overall Interception Success : {success_rate:.1f}% ({total_interceptions}/{self.num_trials})")
        print(f"  - Direct Hit (Hit-to-Kill)   : {direct_hit_rate:.1f}% ({self.results['direct_hits']} trials)")
        print(f"  - Fragment Proximity Hit    : {fragment_hit_rate:.1f}% ({self.results['fragment_hits']} trials)")
        print(f"  - Missed Threats            : {(self.results['misses']/self.num_trials)*100:.1f}% ({self.results['misses']} trials)")
        print(f" Positioning RMS Error        : {mean_pos_error:.3f} m (+/- {std_pos_error:.3f} m)")
        print(f" Self-Healing Recovery Speed   : {mean_healing:.3f} s")
        print(f" Local AI Control Latency     : {mean_ai_lat:.3f} ms (Target < 5.0 ms)")
        print(f" Benchmark Execution Time     : {total_bench_time:.2f} s")
        print("=" * 75)

        return {
            "num_trials": self.num_trials,
            "success_rate_pct": success_rate,
            "direct_hit_rate_pct": direct_hit_rate,
            "fragment_hit_rate_pct": fragment_hit_rate,
            "mean_pos_error_m": mean_pos_error,
            "std_pos_error_m": std_pos_error,
            "mean_healing_time_s": mean_healing,
            "mean_ai_latency_ms": mean_ai_lat
        }

if __name__ == "__main__":
    bench = AccuracyVerificationBenchmark(num_trials=50, sensor_noise_std=0.15)
    bench.execute_benchmark()
