from __future__ import annotations

import argparse
import base64
import dataclasses
import json
import zlib
from typing import Dict, Iterable, List, Tuple


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


def rotate_point(x: float, y: float, rotation_steps: int) -> Tuple[float, float]:
    rotation_steps %= 4
    if rotation_steps == 0:
        return x, y
    if rotation_steps == 1:
        return y, -x
    if rotation_steps == 2:
        return -x, -y
    return -y, x


def rotate_direction(direction: int, rotation_steps: int) -> int:
    return (direction + rotation_steps * 2) % 8


def iter_furnace_positions(count: int) -> Iterable[Tuple[float, float]]:
    for index in range(count):
        yield float(index * 2), 0.0


def iter_belt_positions(count: int) -> Iterable[Tuple[float, float]]:
    for index in range(count * 2):
        yield float(index), 0.0


def build_furnace_entities(count: int, direction: int, furnace: str) -> List[Dict[str, object]]:
    entities: List[Dict[str, object]] = []
    for x, y in iter_furnace_positions(count):
        entities.append(
            {
                "name": furnace,
                "position": {"x": x, "y": y},
                "direction": direction,
            }
        )
    return entities


def build_belt_entities(count: int, belt: str, y_offset: float, direction: int) -> List[Dict[str, object]]:
    entities: List[Dict[str, object]] = []
    for x, _ in iter_belt_positions(count):
        entities.append(
            {
                "name": belt,
                "position": {"x": x, "y": y_offset},
                "direction": direction,
            }
        )
    return entities


def build_inserter_entities(
    count: int, inserter_direction: int, y_offset: float
) -> List[Dict[str, object]]:
    entities: List[Dict[str, object]] = []
    for index in range(count):
        entities.append(
            {
                "name": "inserter",
                "position": {"x": float(index * 2), "y": y_offset},
                "direction": inserter_direction,
            }
        )
    return entities


def build_coal_merge_entities(belt: str) -> List[Dict[str, object]]:
    return [
        {"name": belt, "position": {"x": -1.0, "y": -5.0}, "direction": direction_to_int("north")},
        {"name": belt, "position": {"x": -1.0, "y": -4.0}, "direction": direction_to_int("north")},
        {"name": belt, "position": {"x": -1.0, "y": -3.0}, "direction": direction_to_int("east")},
    ]


def rotation_steps_for_input(input_side: str) -> int:
    order = ["north", "east", "south", "west"]
    return order.index(input_side)


def validate_sides(input_side: str, output_side: str) -> None:
    opposites = {"north": "south", "south": "north", "east": "west", "west": "east"}
    if opposites[input_side] != output_side:
        raise ValueError("Output side must be opposite the input side for the furnace line layout.")


def apply_rotation(
    entities: List[Dict[str, object]], rotation_steps: int
) -> List[Dict[str, object]]:
    rotated: List[Dict[str, object]] = []
    for entity in entities:
        x = float(entity["position"]["x"])
        y = float(entity["position"]["y"])
        new_x, new_y = rotate_point(x, y, rotation_steps)
        rotated_entity = dict(entity)
        rotated_entity["position"] = {"x": new_x, "y": new_y}
        if "direction" in rotated_entity:
            rotated_entity["direction"] = rotate_direction(int(rotated_entity["direction"]), rotation_steps)
        rotated.append(rotated_entity)
    return rotated


def attach_entity_numbers(entities: List[Dict[str, object]]) -> List[Dict[str, object]]:
    for index, entity in enumerate(entities, start=1):
        entity["entity_number"] = index
    return entities


def generate_furnace_blueprint(config: FurnaceLineConfig) -> Dict[str, object]:
    count = calculate_furnace_count(config)
    validate_sides(config.input_side, config.output_side)
    rotation_steps = rotation_steps_for_input(config.input_side)

    furnace_direction = direction_to_int("north")
    belt_direction = direction_to_int("east")
    input_inserter_direction = direction_to_int("south")
    output_inserter_direction = direction_to_int("south")

    entities = [
        *build_furnace_entities(count, furnace_direction, config.furnace),
        *build_belt_entities(count, config.belt, y_offset=-3.0, direction=belt_direction),
        *build_belt_entities(count, config.belt, y_offset=3.0, direction=belt_direction),
        *build_inserter_entities(count, input_inserter_direction, y_offset=-2.0),
        *build_inserter_entities(count, output_inserter_direction, y_offset=2.0),
        *build_coal_merge_entities(config.belt),
    ]

    entities = apply_rotation(entities, rotation_steps)
    entities = attach_entity_numbers(entities)

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

    try:
        blueprint = generate_furnace_blueprint(config)
    except ValueError as exc:
        parser.error(str(exc))
        return
    if args.json:
        print(json.dumps(blueprint, indent=2))
        return

    print(encode_blueprint(blueprint))


if __name__ == "__main__":
    main()
