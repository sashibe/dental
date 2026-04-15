"""
prepare_demo_mesh.py

Loads upper/lower jaw OBJ + FDI label JSON from Teeth3DS+,
simplifies each mesh to ~15,000 faces, transfers vertex labels,
combines both jaws, normalises the result, and writes demo_mesh.json.

Usage:
    python src/preprocessing/prepare_demo_mesh.py \
        --patient 00OMSZGW \
        --teeth3ds datasets/teeth3ds \
        --output docs/demo_mesh.json

Output JSON schema:
    {
      "patient_id": str,
      "stats": {"vertices": int, "faces": int, "upper_teeth": int, "lower_teeth": int},
      "vertices": [[x, y, z], ...],   # float32, normalised to [-1, 1]
      "faces": [[i, j, k], ...],       # int32
      "labels": [fdi_int, ...],        # per-vertex FDI number (0 = gingiva)
      "jaw_ids": [0|1, ...],           # 0 = upper, 1 = lower
      "tooth_centroids": {             # FDI -> [cx, cy, cz]
          "11": [x, y, z], ...
      }
    }
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import cKDTree


def load_mesh_and_labels(obj_path: Path, json_path: Path) -> tuple[trimesh.Trimesh, np.ndarray]:
    """Load a Teeth3DS OBJ file and its per-vertex FDI label array."""
    mesh = trimesh.load(str(obj_path), process=False)
    if not isinstance(mesh, trimesh.Trimesh):
        raise ValueError(f"Expected Trimesh, got {type(mesh)} for {obj_path}")

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    labels = np.array(data["labels"], dtype=np.int32)
    if len(labels) != len(mesh.vertices):
        raise ValueError(
            f"Label count {len(labels)} != vertex count {len(mesh.vertices)} for {obj_path}"
        )
    return mesh, labels


def simplify_mesh(
    mesh: trimesh.Trimesh,
    labels: np.ndarray,
    target_faces: int = 14000,
) -> tuple[trimesh.Trimesh, np.ndarray]:
    """Simplify mesh to ~target_faces and transfer vertex labels via nearest-neighbour."""
    import fast_simplification

    verts = np.array(mesh.vertices, dtype=np.float64)
    faces = np.array(mesh.faces, dtype=np.int64)
    n_faces = len(faces)

    if n_faces <= target_faces:
        return mesh, labels

    target_reduction = 1.0 - target_faces / n_faces
    target_reduction = float(np.clip(target_reduction, 0.0, 0.99))

    verts_out, faces_out = fast_simplification.simplify(verts, faces, target_reduction=target_reduction)
    simple_mesh = trimesh.Trimesh(vertices=verts_out, faces=faces_out, process=False)

    # Transfer labels: nearest neighbour from simplified vertices to original
    tree = cKDTree(verts)
    _, idx = tree.query(verts_out, k=1, workers=-1)
    labels_out = labels[idx]

    return simple_mesh, labels_out


def orient_lower_jaw(
    upper_mesh: trimesh.Trimesh,
    lower_mesh: trimesh.Trimesh,
    upper_labels: np.ndarray | None = None,
    lower_labels: np.ndarray | None = None,
    gap_teeth: float = 0.05,
) -> trimesh.Trimesh:
    """
    Position the lower jaw for a natural open-mouth view.

    In Teeth3DS+, both jaws are scanned in the same coordinate frame
    (closed-occlusion position), so their vertices overlap in Y.  We separate
    them so that:
      - Upper jaw: occlusal surface at low Y (crown tips hang down)
      - Lower jaw: occlusal surface at high Y (crown tips point up)
      - Gap between occlusal surfaces ≈ gap_teeth × one-tooth-height

    gap_teeth=0.9 gives a wide "open mouth" view (dentist angle).
    """
    uv = np.array(upper_mesh.vertices)
    lv = np.array(lower_mesh.vertices)

    # Use tooth vertices only for precise occlusal surface detection
    if upper_labels is not None and np.any(upper_labels != 0):
        u_tooth = uv[np.array(upper_labels) != 0]
    else:
        u_tooth = uv

    if lower_labels is not None and np.any(lower_labels != 0):
        l_tooth = lv[np.array(lower_labels) != 0]
    else:
        l_tooth = lv

    # Upper jaw: crown tips are at MINIMUM Y (hang downward)
    u_occlusal = u_tooth[:, 1].min()
    # Lower jaw: crown tips are at MAXIMUM Y (point upward)
    l_occlusal = l_tooth[:, 1].max()
    # One-tooth-height reference (upper jaw crown Y range)
    tooth_height = u_tooth[:, 1].max() - u_tooth[:, 1].min()

    # Target: lower occlusal surface placed gap_teeth × tooth_height below upper
    target_l_occlusal = u_occlusal - gap_teeth * tooth_height
    offset = target_l_occlusal - l_occlusal

    moved = lower_mesh.copy()
    moved.vertices[:, 1] += offset
    return moved


def normalise_combined(
    vertices: np.ndarray,
) -> tuple[np.ndarray, float, np.ndarray]:
    """Centre and scale to fit in a unit sphere; return (normalised, scale, centre)."""
    centre = (vertices.max(axis=0) + vertices.min(axis=0)) / 2.0
    v = vertices - centre
    scale = np.abs(v).max()
    if scale > 0:
        v /= scale
    return v.astype(np.float32), float(scale), centre


def compute_tooth_centroids(vertices: np.ndarray, labels: np.ndarray) -> dict[str, list[float]]:
    """Return per-FDI centroid (excluding gingiva label 0)."""
    centroids: dict[str, list[float]] = {}
    for fdi in np.unique(labels):
        if fdi == 0:
            continue
        mask = labels == fdi
        c = vertices[mask].mean(axis=0).tolist()
        centroids[str(int(fdi))] = [round(float(x), 5) for x in c]
    return centroids


def build_demo_mesh(
    patient_id: str,
    teeth3ds_dir: Path,
    output_path: Path,
    target_faces_per_jaw: int = 14000,
) -> None:
    upper_obj = teeth3ds_dir / "upper" / patient_id / f"{patient_id}_upper.obj"
    upper_json = teeth3ds_dir / "upper" / patient_id / f"{patient_id}_upper.json"
    lower_obj = teeth3ds_dir / "lower" / patient_id / f"{patient_id}_lower.obj"
    lower_json = teeth3ds_dir / "lower" / patient_id / f"{patient_id}_lower.json"

    for p in (upper_obj, upper_json, lower_obj, lower_json):
        if not p.exists():
            raise FileNotFoundError(f"Missing: {p}")

    print(f"Loading upper jaw from {upper_obj} …")
    upper_mesh, upper_labels = load_mesh_and_labels(upper_obj, upper_json)
    print(f"  {len(upper_mesh.vertices):,} vertices, {len(upper_mesh.faces):,} faces")

    print(f"Loading lower jaw from {lower_obj} …")
    lower_mesh, lower_labels = load_mesh_and_labels(lower_obj, lower_json)
    print(f"  {len(lower_mesh.vertices):,} vertices, {len(lower_mesh.faces):,} faces")

    print("Simplifying upper jaw …")
    upper_simple, upper_labels_s = simplify_mesh(upper_mesh, upper_labels, target_faces_per_jaw)
    print(f"  → {len(upper_simple.vertices):,} vertices, {len(upper_simple.faces):,} faces")

    print("Simplifying lower jaw …")
    lower_simple, lower_labels_s = simplify_mesh(lower_mesh, lower_labels, target_faces_per_jaw)
    print(f"  → {len(lower_simple.vertices):,} vertices, {len(lower_simple.faces):,} faces")

    # ── Separate jaws and remap axes ─────────────────────────────────────────
    # Teeth3DS coordinate system (confirmed by inspection):
    #   X = left-right  (~62 mm)
    #   Y = front-back, anterior-posterior  (~55 mm)
    #   Z = vertical  (~27 mm); larger Z (less negative) = toward bite surface
    #
    # In closed occlusion both jaws share the same Z range.
    # Separation: upper Z += JAW_SEP_MM, lower Z -= JAW_SEP_MM.
    #
    # Three.js Y-up remapping:
    #   three.x =  orig.x              (left-right)
    #   three.z = -orig.y              (front teeth face camera at +Z)
    #   Upper:  three.y = -(orig.z)    (negate Z so crown tips face DOWN)
    #   Lower:  three.y =   orig.z     (crown tips already face UP)

    JAW_SEP_MM = 12.0

    upper_v = np.array(upper_simple.vertices, dtype=np.float64)
    lower_v = np.array(lower_simple.vertices, dtype=np.float64)
    upper_f = np.array(upper_simple.faces, dtype=np.int32)
    lower_f = np.array(lower_simple.faces, dtype=np.int32) + len(upper_v)

    print(f"Separating jaws by +-{JAW_SEP_MM:.0f} mm along Z ...")
    upper_v[:, 2] += JAW_SEP_MM
    lower_v[:, 2] -= JAW_SEP_MM

    def _remap_upper(v: np.ndarray) -> np.ndarray:
        r = np.empty_like(v)
        r[:, 0] =  v[:, 0]    # X  → X
        r[:, 1] = -v[:, 2]    # Z  → -Y  (flip: upper crown tips face downward)
        r[:, 2] = -v[:, 1]    # Y  → -Z  (front teeth toward camera)
        return r

    def _remap_lower(v: np.ndarray) -> np.ndarray:
        r = np.empty_like(v)
        r[:, 0] =  v[:, 0]    # X  → X
        r[:, 1] =  v[:, 2]    # Z  → Y
        r[:, 2] = -v[:, 1]    # Y  → -Z
        return r

    upper_v = _remap_upper(upper_v)
    lower_v = _remap_lower(lower_v)

    # Align upper jaw so crown tips (MIN Y of upper teeth after flip) meet
    # lower crown tips (MAX Y of lower teeth) with a 1 mm clearance gap.
    # This makes slider=0 (jaw rotation angle=0) the closed-bite position.
    # The slider opening animation then rotates the lower jaw from this state.
    CLOSED_BITE_GAP_MM = 1.0   # 1 mm clearance prevents z-fighting at full close
    ut_mask_local = upper_labels_s != 0
    lt_mask_local = lower_labels_s != 0
    upper_crown_y = upper_v[ut_mask_local, 1].min()
    lower_crown_y = lower_v[lt_mask_local, 1].max()
    shift_y = (lower_crown_y + CLOSED_BITE_GAP_MM) - upper_crown_y
    upper_v[:, 1] += shift_y
    print(f"  Upper jaw Y shift: {shift_y:.1f} mm  "
          f"| upper crown tip Y: {upper_crown_y+shift_y:.3f}  "
          f"| lower crown tip Y: {lower_crown_y:.3f}  "
          f"| gap: {CLOSED_BITE_GAP_MM:.1f} mm")

    combined_v = np.vstack([upper_v, lower_v])
    combined_f = np.vstack([upper_f, lower_f])
    combined_labels = np.concatenate([upper_labels_s, lower_labels_s])
    jaw_ids = np.array(
        [0] * len(upper_v) + [1] * len(lower_v), dtype=np.int8
    )

    print("Normalising …")
    norm_v, scale, centre = normalise_combined(combined_v)

    # ── Verify placement ──────────────────────────────────────────────────────
    ut_mask = (jaw_ids == 0) & (combined_labels != 0)
    lt_mask = (jaw_ids == 1) & (combined_labels != 0)
    u_y_avg = norm_v[ut_mask, 1].mean()
    l_y_avg = norm_v[lt_mask, 1].mean()
    u_y_min = norm_v[ut_mask, 1].min()
    l_y_max = norm_v[lt_mask, 1].max()
    sep_ok = "OK separated" if u_y_min > l_y_max else "!! overlapping"
    print(f"  Upper tooth Y avg = {u_y_avg:+.3f}  (want positive)")
    print(f"  Lower tooth Y avg = {l_y_avg:+.3f}  (want negative)")
    print(f"  Upper Y min = {u_y_min:.3f}  |  Lower Y max = {l_y_max:.3f}  --> {sep_ok}")

    upper_teeth_count = len(set(upper_labels_s.tolist()) - {0})
    lower_teeth_count = len(set(lower_labels_s.tolist()) - {0})

    print("Computing tooth centroids …")
    centroids = compute_tooth_centroids(norm_v, combined_labels)

    # Flatten vertices/faces to 1-D arrays for compact JSON representation.
    # Coordinates stored as 4-decimal-place floats; indices as plain integers.
    verts_flat = [round(float(v), 4) for row in norm_v for v in row]
    faces_flat = [int(i) for row in combined_f for i in row]

    result = {
        "patient_id": patient_id,
        "stats": {
            "vertices": int(len(norm_v)),
            "faces": int(len(combined_f)),
            "upper_teeth": upper_teeth_count,
            "lower_teeth": lower_teeth_count,
        },
        "vertices": verts_flat,
        "faces": faces_flat,
        "labels": combined_labels.tolist(),
        "jaw_ids": jaw_ids.tolist(),
        "tooth_centroids": centroids,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, separators=(",", ":"))

    size_kb = output_path.stat().st_size / 1024
    print(f"\nSaved {output_path}  ({size_kb:.0f} KB)")
    print(f"  {result['stats']['vertices']:,} vertices | {result['stats']['faces']:,} faces")
    print(f"  Upper teeth: {upper_teeth_count}  Lower teeth: {lower_teeth_count}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare demo mesh for KIREI demo")
    parser.add_argument("--patient", default="00OMSZGW", help="Patient ID (default: 00OMSZGW)")
    parser.add_argument(
        "--teeth3ds", default="datasets/teeth3ds", help="Path to Teeth3DS+ root directory"
    )
    parser.add_argument("--output", default="docs/demo_mesh.json", help="Output JSON path")
    parser.add_argument(
        "--target-faces", type=int, default=14000, help="Target faces per jaw after simplification"
    )
    args = parser.parse_args()

    build_demo_mesh(
        patient_id=args.patient,
        teeth3ds_dir=Path(args.teeth3ds),
        output_path=Path(args.output),
        target_faces_per_jaw=args.target_faces,
    )


if __name__ == "__main__":
    main()
