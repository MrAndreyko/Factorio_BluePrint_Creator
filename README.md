# Factorio Blueprint Creator

This repository contains the beginnings of an external blueprint generator app. The current focus is a **furnace-line planner** that can be run from the CLI to generate a blueprint string (or raw JSON) for Factorio.

## Why start external?
- Faster iteration on UI and data models.
- Easier validation of ratios and math.
- The logic can be ported into a Factorio mod later.

## Current capabilities
- Calculates the number of furnaces needed to saturate a selected belt.
- Allows choosing furnace type, belt type, and basic metadata for input/output sides.
- Outputs a blueprint string or raw JSON.

## Usage

```bash
python3 src/blueprint_generator.py --furnace stone-furnace --belt transport-belt
```

Output raw JSON for inspection:

```bash
python3 src/blueprint_generator.py --json
```

## Next steps (planned)
- Add inserters and belts based on input/output direction.
- Add layout previews (grid visualization).
- Add crafting-chain ratio calculations (e.g., green circuits).
- Build a web UI around the generator.
