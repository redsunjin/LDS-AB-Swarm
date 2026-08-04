from src.core.mesh_generator import ThreatTrajectory, MeshGenerator

__all__ = ["ThreatTrajectory", "MeshGenerator"]

if __name__ == "__main__":
    import numpy as np
    
    print("Testing Multi-Layer Multi-Angle MeshGenerator...")
    weaving_threat = ThreatTrajectory.create_weaving_sinusoidal(
        start_pos=[200.0, 0.0, 50.0],
        base_velocity=[-35.0, 0.0, 0.0],
        amplitude=10.0
    )
    generator = MeshGenerator(default_spacing=6.0)
    nodes = generator.generate_mesh(
        trajectory=weaving_threat,
        time_to_intercept=3.0,
        grid_shape=(5, 5),
        depth_layers=2,
        layer_stagger=True,
        pitch_offset_deg=15.0
    )
    print(f"Successfully generated {nodes.shape[0]} 3D multi-layer staggered nodes!")
