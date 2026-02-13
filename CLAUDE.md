# Spur Gear Solver

## Project Structure

- `src/spur_gear_solver/` — Main package
  - `models.py` — Data classes: SingleGear, CompoundGear, Stage, Solution
  - `loader.py` — JSON gear inventory loading and validation
  - `solver.py` — Core solver algorithm (brute-force enumeration with module matching)
  - `cli.py` — Command-line interface with formatted output

## Key Concepts

- **Single gear**: `[teeth, module]` — a basic spur gear
- **Compound gear**: `[[big_teeth, big_mod], [small_teeth, small_mod]]` — two gears fixed on the same axis, bigger diameter first
- **Gear train**: `[single, compound*, single]` — first and last gears are always single-stage
- Meshing gears must have the same module
- Ratio is always >= 1.0 (reduction only)
- Gears from inventory can be reused unlimited times

## Algorithm

1. Group gears by module
2. Enumerate 1-stage solutions (single → single, same module)
3. Enumerate multi-stage solutions by building compound gear chains with matching modules
4. Sort all valid solutions by distance to target ratio
5. Return top N

## Development

- Install: `pip install -e .`
- Run: `spur-gear-solve --ratio 16.67 --gears example_gears.json`
- Python >= 3.10 required
- No external dependencies
