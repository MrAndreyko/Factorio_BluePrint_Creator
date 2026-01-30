# Factorio Blueprint Creator

This repository contains the beginnings of an external blueprint generator app. The current focus is a **furnace-line planner** that can be run from the CLI to generate a blueprint string (or raw JSON) for Factorio.

## Why start external?
- Faster iteration on UI and data models.
- Easier validation of ratios and math.
- The logic can be ported into a Factorio mod later.

## Current capabilities
- Calculates the number of furnaces needed to saturate a selected belt.
- Places furnaces, belts, and inserters for a simple line layout.
- Allows choosing furnace type, belt type, and input/output sides (must be opposite).
- Adds a coal side-loading stub that merges onto the input belt.
- Outputs a blueprint string or raw JSON.

## Usage

```bash
python3 src/blueprint_generator.py --furnace stone-furnace --belt transport-belt
```

Example with explicit sides:

```bash
python3 src/blueprint_generator.py --input-side east --output-side west --json
```

Output raw JSON for inspection:

```bash
python3 src/blueprint_generator.py --json
```

## Next steps (planned)
- Add splitters/mergers and belt balancers for multi-lane inputs.
- Add layout previews (grid visualization).
- Add crafting-chain ratio calculations (e.g., green circuits).
- Build a web UI around the generator.
