"""STL/OBJ viewer and mesh info reporter for Teeth3DS+ dataset.

Usage:
    python view_stl.py <path_to_stl_or_obj>
    python view_stl.py <path_to_stl_or_obj> --no-display
"""

import argparse
import sys
from pathlib import Path


def print_mesh_info(mesh_path: Path) -> None:
    """Print mesh statistics: vertex count, face count, bounding box."""
    import trimesh

    mesh = trimesh.load(str(mesh_path), force="mesh")

    if not isinstance(mesh, trimesh.Trimesh):
        # Some OBJ files load as Scene; extract the first geometry
        if hasattr(mesh, "geometry") and mesh.geometry:
            mesh = next(iter(mesh.geometry.values()))
        else:
            print(f"ERROR: Could not load mesh from {mesh_path}", file=sys.stderr)
            sys.exit(1)

    bb_min = mesh.bounds[0]
    bb_max = mesh.bounds[1]
    bb_size = bb_max - bb_min

    print(f"File       : {mesh_path}")
    print(f"Vertices   : {len(mesh.vertices):,}")
    print(f"Faces      : {len(mesh.faces):,}")
    print(f"Watertight : {mesh.is_watertight}")
    print(f"BBox min   : [{bb_min[0]:.3f}, {bb_min[1]:.3f}, {bb_min[2]:.3f}]")
    print(f"BBox max   : [{bb_max[0]:.3f}, {bb_max[1]:.3f}, {bb_max[2]:.3f}]")
    print(f"BBox size  : [{bb_size[0]:.3f}, {bb_size[1]:.3f}, {bb_size[2]:.3f}] mm")
    print(f"Volume     : {mesh.volume:.2f} mm³" if mesh.is_watertight else "Volume     : N/A (non-watertight)")


def display_mesh_open3d(mesh_path: Path) -> None:
    """Display mesh using Open3D interactive viewer."""
    import open3d as o3d

    print(f"\nLaunching Open3D viewer for {mesh_path.name} ...")
    print("(Press Q or Escape to close)")

    mesh = o3d.io.read_triangle_mesh(str(mesh_path))
    mesh.compute_vertex_normals()

    o3d.visualization.draw_geometries(
        [mesh],
        window_name=mesh_path.name,
        width=1024,
        height=768,
    )


def display_mesh_pyvista(mesh_path: Path) -> None:
    """Display mesh using PyVista as fallback."""
    import pyvista as pv

    print(f"\nLaunching PyVista viewer for {mesh_path.name} ...")
    print("(Close the window to exit)")

    mesh = pv.read(str(mesh_path))
    plotter = pv.Plotter(window_size=[1024, 768], title=mesh_path.name)
    plotter.add_mesh(mesh, color="ivory", show_edges=False, smooth_shading=True)
    plotter.add_axes()
    plotter.show()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Display STL/OBJ mesh info and 3D visualization."
    )
    parser.add_argument("mesh_path", type=Path, help="Path to STL or OBJ file")
    parser.add_argument(
        "--no-display",
        action="store_true",
        help="Only print mesh info, skip 3D viewer",
    )
    parser.add_argument(
        "--viewer",
        choices=["open3d", "pyvista", "auto"],
        default="auto",
        help="Choose 3D viewer backend (default: auto)",
    )
    args = parser.parse_args()

    mesh_path: Path = args.mesh_path.resolve()

    if not mesh_path.exists():
        print(f"ERROR: File not found: {mesh_path}", file=sys.stderr)
        sys.exit(1)

    if mesh_path.suffix.lower() not in {".stl", ".obj"}:
        print(f"WARNING: Unexpected extension '{mesh_path.suffix}'. Proceeding anyway.")

    print_mesh_info(mesh_path)

    if args.no_display:
        return

    viewer = args.viewer
    if viewer == "auto":
        # Prefer open3d; fall back to pyvista
        try:
            import open3d  # noqa: F401
            viewer = "open3d"
        except ImportError:
            viewer = "pyvista"

    if viewer == "open3d":
        try:
            display_mesh_open3d(mesh_path)
        except Exception as exc:
            print(f"open3d display failed ({exc}), falling back to pyvista.")
            display_mesh_pyvista(mesh_path)
    else:
        display_mesh_pyvista(mesh_path)


if __name__ == "__main__":
    main()
