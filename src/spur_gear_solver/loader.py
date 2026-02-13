import json
from pathlib import Path

from .models import SingleGear, CompoundGear


def load_gears(path: str | Path) -> list[SingleGear | CompoundGear]:
    """Load and validate gear inventory from a JSON file."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Gear file not found: {path}")

    with open(path) as f:
        data = json.load(f)

    if "gears" not in data:
        raise ValueError("JSON must contain a 'gears' key")

    gears: list[SingleGear | CompoundGear] = []
    seen: set[tuple] = set()

    for i, entry in enumerate(data["gears"]):
        gear = _parse_gear(entry, i)
        key = _gear_key(gear)
        if key not in seen:
            seen.add(key)
            gears.append(gear)

    return gears


def _parse_single_values(entry, label) -> tuple[int, float]:
    """Parse and validate [teeth, module] values."""
    if not isinstance(entry, list) or len(entry) != 2:
        raise ValueError(f"Gear {label}: expected [teeth, module], got {entry}")

    teeth_raw, module_raw = entry

    if not isinstance(teeth_raw, (int, float)) or not isinstance(module_raw, (int, float)):
        raise ValueError(f"Gear {label}: teeth and module must be numbers, got {entry}")

    teeth = int(teeth_raw)
    module = float(module_raw)

    if teeth <= 0:
        raise ValueError(f"Gear {label}: teeth must be positive, got {teeth}")
    if module <= 0:
        raise ValueError(f"Gear {label}: module must be positive, got {module}")

    return teeth, module


def _parse_gear(entry, index: int) -> SingleGear | CompoundGear:
    """Parse a gear entry — either single or compound.

    Formats:
        Single:   ["name", teeth, module]
        Compound: ["name", [teeth, module], [teeth, module]]
    """
    if not isinstance(entry, list) or len(entry) != 3:
        raise ValueError(
            f"Gear {index}: expected [name, teeth, module] or "
            f"[name, [teeth, module], [teeth, module]], got {entry}"
        )

    name = entry[0]
    if not isinstance(name, str):
        raise ValueError(f"Gear {index}: first element must be a name string, got {name!r}")

    # Single gear: ["name", teeth, module]
    if isinstance(entry[1], (int, float)) and isinstance(entry[2], (int, float)):
        teeth, module = _parse_single_values(entry[1:], index)
        return SingleGear(name=name, teeth=teeth, module=module)

    # Compound gear: ["name", [teeth, module], [teeth, module]]
    if isinstance(entry[1], list) and isinstance(entry[2], list):
        big_teeth, big_module = _parse_single_values(entry[1], f"{index}[big]")
        small_teeth, small_module = _parse_single_values(entry[2], f"{index}[small]")

        big = SingleGear(name=f"{name}/big", teeth=big_teeth, module=big_module)
        small = SingleGear(name=f"{name}/small", teeth=small_teeth, module=small_module)

        if big.diameter() <= small.diameter():
            raise ValueError(
                f"Gear {index} ({name}): the bigger wheel must be in first position. "
                f"First stage diameter: {big.diameter():.2f}mm, "
                f"second stage diameter: {small.diameter():.2f}mm"
            )

        return CompoundGear(name=name, big=big, small=small)

    raise ValueError(
        f"Gear {index}: invalid format {entry}. Expected "
        f"[name, teeth, module] or [name, [teeth, module], [teeth, module]]"
    )


def _gear_key(gear: SingleGear | CompoundGear) -> tuple:
    """Return a hashable key for deduplication."""
    if isinstance(gear, SingleGear):
        return ("single", gear.teeth, gear.module)
    return ("compound", gear.big.teeth, gear.big.module, gear.small.teeth, gear.small.module)
