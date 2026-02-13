from collections import defaultdict

from .models import SingleGear, CompoundGear, Stage, Solution


def solve(
    gears: list[SingleGear | CompoundGear],
    target_ratio: float,
    max_stages: int = 4,
    top_n: int = 3,
) -> list[Solution]:
    """Find the best gear combinations matching the target reduction ratio.

    Args:
        gears: Available gear inventory (singles and compounds).
        target_ratio: Desired reduction ratio (>= 1.0).
        max_stages: Maximum number of reduction stages to explore.
        top_n: Number of best solutions to return.

    Returns:
        List of up to top_n Solutions sorted by closeness to target_ratio.
    """
    if target_ratio < 1.0:
        raise ValueError("Target ratio must be >= 1.0 (reduction only)")

    singles = [g for g in gears if isinstance(g, SingleGear)]
    compounds = [g for g in gears if isinstance(g, CompoundGear)]

    # Group singles by module for fast lookup
    singles_by_mod: dict[float, list[SingleGear]] = defaultdict(list)
    for g in singles:
        singles_by_mod[g.module].append(g)

    # Group compounds by input module (big wheel module)
    compounds_by_input_mod: dict[float, list[CompoundGear]] = defaultdict(list)
    for g in compounds:
        compounds_by_input_mod[g.big.module].append(g)

    solutions: list[Solution] = []

    # --- 1-stage solutions: single -> single (same module) ---
    for mod, mod_singles in singles_by_mod.items():
        for driver in mod_singles:
            for driven in mod_singles:
                ratio = driven.teeth / driver.teeth
                if ratio >= 1.0:
                    stage = Stage(
                        driver_teeth=driver.teeth,
                        driven_teeth=driven.teeth,
                        module=mod,
                        ratio=ratio,
                    )
                    solutions.append(
                        Solution(gears=[driver, driven], ratio=ratio, stages=[stage])
                    )

    # --- Multi-stage solutions: single -> compound(s) -> single ---
    for num_compounds in range(1, max_stages):
        for chain in _build_compound_chains(compounds_by_input_mod, num_compounds):
            input_mod = chain[0].big.module
            output_mod = chain[-1].small.module

            for driver in singles_by_mod.get(input_mod, []):
                for driven in singles_by_mod.get(output_mod, []):
                    stages = _compute_stages(driver, chain, driven)

                    overall_ratio = 1.0
                    for s in stages:
                        overall_ratio *= s.ratio

                    if overall_ratio >= 1.0:
                        gear_list = [driver] + list(chain) + [driven]
                        solutions.append(
                            Solution(
                                gears=gear_list,
                                ratio=overall_ratio,
                                stages=stages,
                            )
                        )

    # Sort by closeness to target ratio
    solutions.sort(key=lambda s: abs(s.ratio - target_ratio))

    # Deduplicate identical gear trains
    seen: set[tuple[str, ...]] = set()
    unique: list[Solution] = []
    for s in solutions:
        key = tuple(str(g) for g in s.gears)
        if key not in seen:
            seen.add(key)
            unique.append(s)
        if len(unique) >= top_n:
            break

    return unique


def _build_compound_chains(
    compounds_by_input_mod: dict[float, list[CompoundGear]],
    length: int,
    output_mod: float | None = None,
):
    """Recursively build valid chains of compound gears with matching modules.

    Yields tuples of CompoundGear where each gear's small.module matches the
    next gear's big.module.
    """
    if length == 0:
        yield ()
        return

    if output_mod is None:
        # Starting point: try all available compounds
        for compounds in compounds_by_input_mod.values():
            for c in compounds:
                for rest in _build_compound_chains(
                    compounds_by_input_mod, length - 1, c.small.module
                ):
                    yield (c,) + rest
    else:
        # Continue chain: input module must match previous output module
        for c in compounds_by_input_mod.get(output_mod, []):
            for rest in _build_compound_chains(
                compounds_by_input_mod, length - 1, c.small.module
            ):
                yield (c,) + rest


def _compute_stages(
    driver: SingleGear,
    chain: tuple[CompoundGear, ...],
    driven: SingleGear,
) -> list[Stage]:
    """Compute the stage-by-stage ratios for a complete gear train."""
    stages: list[Stage] = []

    # First stage: driver -> compound[0].big
    stages.append(
        Stage(
            driver_teeth=driver.teeth,
            driven_teeth=chain[0].big.teeth,
            module=driver.module,
            ratio=chain[0].big.teeth / driver.teeth,
        )
    )

    # Intermediate stages: compound[i].small -> compound[i+1].big
    for i in range(len(chain) - 1):
        stages.append(
            Stage(
                driver_teeth=chain[i].small.teeth,
                driven_teeth=chain[i + 1].big.teeth,
                module=chain[i].small.module,
                ratio=chain[i + 1].big.teeth / chain[i].small.teeth,
            )
        )

    # Last stage: compound[-1].small -> driven
    stages.append(
        Stage(
            driver_teeth=chain[-1].small.teeth,
            driven_teeth=driven.teeth,
            module=chain[-1].small.module,
            ratio=driven.teeth / chain[-1].small.teeth,
        )
    )

    return stages
