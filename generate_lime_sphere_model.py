import json
import math
from pathlib import Path


PACK_ROOT = Path(__file__).resolve().parent
MODEL_PATH = PACK_ROOT / "assets" / "hns" / "models" / "block" / "lime_sphere.json"
BLOCKSTATE_PATH = PACK_ROOT / "assets" / "minecraft" / "blockstates" / "structure_void.json"

# Higher values make the sphere smoother, but also make the model heavier.
RESOLUTION = 18
OUTER_RADIUS = 8.0
SHELL_THICKNESS = 0.9


def is_shell_voxel(x: int, y: int, z: int) -> bool:
    step = 16.0 / RESOLUTION
    cx = (x + 0.5) * step - 8.0
    cy = (y + 0.5) * step - 8.0
    cz = (z + 0.5) * step - 8.0
    distance = math.sqrt(cx * cx + cy * cy + cz * cz)
    return OUTER_RADIUS - SHELL_THICKNESS <= distance <= OUTER_RADIUS


def face(texture: str = "#all") -> dict:
    return {"texture": texture, "uv": [0, 0, 16, 16]}


def main() -> None:
    step = 16.0 / RESOLUTION
    voxels = {
        (x, y, z)
        for x in range(RESOLUTION)
        for y in range(RESOLUTION)
        for z in range(RESOLUTION)
        if is_shell_voxel(x, y, z)
    }

    directions = {
        "east": (1, 0, 0),
        "west": (-1, 0, 0),
        "up": (0, 1, 0),
        "down": (0, -1, 0),
        "south": (0, 0, 1),
        "north": (0, 0, -1),
    }

    elements = []
    for x, y, z in sorted(voxels):
        faces = {}
        for name, (dx, dy, dz) in directions.items():
            if (x + dx, y + dy, z + dz) not in voxels:
                faces[name] = face()

        if not faces:
            continue

        elements.append(
            {
                "from": [round(x * step, 4), round(y * step, 4), round(z * step, 4)],
                "to": [round((x + 1) * step, 4), round((y + 1) * step, 4), round((z + 1) * step, 4)],
                "shade": False,
                "faces": faces,
            }
        )

    model = {
        "credit": "Generated for HideNSeek particle_sphere.",
        "ambientocclusion": False,
        "render_type": "minecraft:translucent",
        "textures": {
            "particle": "minecraft:block/lime_stained_glass",
            "all": "minecraft:block/lime_stained_glass",
        },
        "elements": elements,
    }

    blockstate = {
        "variants": {
            "": {
                "model": "hns:block/lime_sphere"
            }
        }
    }

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.write_text(json.dumps(model, indent=2) + "\n", encoding="utf-8")
    BLOCKSTATE_PATH.write_text(json.dumps(blockstate, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {MODEL_PATH.relative_to(PACK_ROOT)} with {len(elements)} shell voxels")
    print(f"Wrote {BLOCKSTATE_PATH.relative_to(PACK_ROOT)} -> hns:block/lime_sphere")


if __name__ == "__main__":
    main()
