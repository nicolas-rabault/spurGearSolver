# Spur Gear Solver

Find the best spur gear combinations for a target reduction ratio using the gears you have.

## Installation

```bash
pip install -e .
```

## Gear Inventory

Create a `gears.json` file listing all your available gears. Each gear has a **name** (reference string) followed by its specs:

- **Single gear** — `["name", teeth, module]`
- **Compound gear** (two stages fixed on the same axis) — `["name", [teeth, module], [teeth, module]]`

For compound gears, the **bigger wheel** (larger diameter = teeth x module) must be listed **first**.

### Example `gears.json`

```json
{
    "gears": [
        ["S05-12", 12, 0.5],
        ["S05-20", 20, 0.5],
        ["S05-45", 45, 0.5],
        ["S10-9", 9, 1.0],
        ["S10-40", 40, 1.0],
        ["C-45/9", [45, 0.5], [9, 1.0]],
        ["C-36/15", [36, 0.5], [15, 1.0]]
    ]
}
```

## Usage

```bash
spur-gear-solve --ratio 16.67
```

By default the tool looks for `gears.json` in the current directory. Use `--gears` to specify a different file.

### Options

| Option | Short | Default | Description |
|---|---|---|---|
| `--ratio` | `-r` | *(required)* | Target reduction ratio (>= 1.0) |
| `--gears` | `-g` | `gears.json` | Path to your gears JSON file |
| `--max-stages` | `-s` | 4 | Maximum number of reduction stages |
| `--top` | `-n` | 3 | Number of solutions to display |

### Example Output

```
  ╔══════════════════════════════════════════════════════╗
  ║                   Spur Gear Solver                   ║
  ╠══════════════════════════════════════════════════════╣
  ║  Target ratio  :  16.6700                            ║
  ║  Inventory     :  8 single, 2 compound gear(s)       ║
  ║  Max stages    :  4                                  ║
  ╚══════════════════════════════════════════════════════╝

  Top 3 solution(s):

  #1  Ratio: 16.6667  (error: -0.02%)
  ──────────────────────────────────────────────────────
    Stage 1  │  module 0.5    │   12T  ->   45T  │  x3.7500
    Stage 2  │  module 1.0    │    9T  ->   40T  │  x4.4444

    S05-12  ->  C-45/9  ->  S10-40
```

## How It Works

The solver enumerates all valid gear trains from your inventory:

- **1-stage**: two single gears with the same module
- **2-stage**: single → compound → single (modules match at each mesh point)
- **N-stage**: single → compound → ... → compound → single

It ranks every valid combination by how close its ratio is to your target and returns the best matches.
