from __future__ import annotations

import argparse
import base64
import dataclasses
import json
import zlib
from typing import Dict, List


BELT_THROUGHPUT_ITEMS_PER_SEC = {
    "transport-belt": 15.0,
    "fast-transport-belt": 30.0,
    "express-transport-belt": 45.0,
}

FURNACE_SPEED = {
    "stone-furnace": 1.0,
    "steel-furnace": 2.0,
    "electric-furnace": 2.0,
}

SMELTING_TIME_SECONDS = 3.2


@dataclasses.dataclass
class FurnaceLineConfig:
    furnace: str = "stone-furnace"
    belt: str = "transport-belt"
    length: int | None = None
    input_side: str = "north"
    output_side: str = "south"
    blueprint_label: str = "Furnace line"


def clamp_length(value: int) -> int:
    return max(1, min(value, 200))


def furnaces_per_full_belt(furnace: str, belt: str) -> float:
    belt_rate = BELT_THROUGHPUT_ITEMS_PER_SEC[belt]
    furnace_rate = FURNACE_SPEED[furnace] / SMELTING_TIME_SECONDS
    return belt_rate / furnace_rate


def calculate_furnace_count(config: FurnaceLineConfig) -> int:
    if config.length is not None:
        return clamp_length(config.length)

    furnaces_needed = furnaces_per_full_belt(config.furnace, config.belt)
    return clamp_length(int(round(furnaces_needed)))


def direction_to_int(direction: str) -> int:
    mapping = {
        "north": 0,
        "east": 2,
        "south": 4,
        "west": 6,
    }
    return mapping[direction]


def build_furnace_entities(count: int, direction: int, furnace: str) -> List[Dict[str, object]]:
    entities: List[Dict[str, object]] = []
    for index in range(count):
        entities.append(
            {
                "entity_number": index + 1,
                "name": furnace,
                "position": {"x": float(index * 2), "y": 0.0},
                "direction": direction,
            }
        )
    return entities


def generate_furnace_blueprint(config: FurnaceLineConfig) -> Dict[str, object]:
    count = calculate_furnace_count(config)
    direction = direction_to_int("north")
    entities = build_furnace_entities(count, direction, config.furnace)

    return {
        "blueprint": {
            "label": config.blueprint_label,
            "item": "blueprint",
            "version": 0,
            "entities": entities,
            "icons": [
                {
                    "signal": {"type": "item", "name": config.furnace},
                    "index": 1,
                }
            ],
            "metadata": {
                "input_side": config.input_side,
                "output_side": config.output_side,
                "belt": config.belt,
                "furnace_count": count,
            },
        }
    }


def encode_blueprint(blueprint: Dict[str, object]) -> str:
    raw = json.dumps(blueprint, separators=(",", ":")).encode("utf-8")
    compressed = zlib.compress(raw, level=9)
    encoded = base64.b64encode(compressed).decode("utf-8")
    return f"0{encoded}"


def build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a furnace line blueprint string.")
    parser.add_argument("--furnace", default="stone-furnace", choices=sorted(FURNACE_SPEED.keys()))
    parser.add_argument("--belt", default="transport-belt", choices=sorted(BELT_THROUGHPUT_ITEMS_PER_SEC.keys()))
    parser.add_argument("--length", type=int)
    parser.add_argument("--input-side", default="north", choices=["north", "east", "south", "west"])
    parser.add_argument("--output-side", default="south", choices=["north", "east", "south", "west"])
    parser.add_argument("--label", default="Furnace line")
    parser.add_argument("--json", action="store_true", help="Output raw blueprint JSON instead of encoded string.")
    return parser


def main() -> None:
    parser = build_cli_parser()
    args = parser.parse_args()

    config = FurnaceLineConfig(
        furnace=args.furnace,
        belt=args.belt,
        length=args.length,
        input_side=args.input_side,
        output_side=args.output_side,
        blueprint_label=args.label,
    )

    blueprint = generate_furnace_blueprint(config)
    if args.json:
        print(json.dumps(blueprint, indent=2))
        return

    print(encode_blueprint(blueprint))


if __name__ == "__main__":
    main()
