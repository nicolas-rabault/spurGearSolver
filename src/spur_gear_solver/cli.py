import argparse
import json
import sys

from .loader import load_gears
from .models import SingleGear, CompoundGear, Solution
from .solver import solve


def _format_gear_train(solution: Solution) -> str:
    return "  ->  ".join(str(g) for g in solution.gears)


def _print_solution(rank: int, solution: Solution, target_ratio: float):
    error_pct = ((solution.ratio - target_ratio) / target_ratio) * 100

    print(f"  #{rank}  Ratio: {solution.ratio:.4f}  (error: {error_pct:+.2f}%)")
    print(f"  {'─' * 54}")

    for i, stage in enumerate(solution.stages, 1):
        mod_str = f"{stage.module}"
        print(
            f"    Stage {i}  │  module {mod_str:<5}  │  "
            f"{stage.driver_teeth:>3}T  ->  {stage.driven_teeth:>3}T  │  "
            f"x{stage.ratio:.4f}"
        )

    print()
    print(f"    {_format_gear_train(solution)}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Find optimal spur gear combinations for a target reduction ratio",
    )
    parser.add_argument(
        "--ratio",
        "-r",
        type=float,
        required=True,
        help="Target reduction ratio (>= 1.0)",
    )
    parser.add_argument(
        "--gears",
        "-g",
        type=str,
        default="gears.json",
        help="Path to JSON file listing available gears (default: gears.json)",
    )
    parser.add_argument(
        "--max-stages",
        "-s",
        type=int,
        default=4,
        help="Maximum number of reduction stages (default: 4)",
    )
    parser.add_argument(
        "--top",
        "-n",
        type=int,
        default=3,
        help="Number of solutions to display (default: 3)",
    )

    args = parser.parse_args()

    if args.ratio < 1.0:
        print("Error: ratio must be >= 1.0 (reduction only)")
        sys.exit(1)

    try:
        gears = load_gears(args.gears)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        print(f"Error loading gears: {e}")
        sys.exit(1)

    singles_count = sum(1 for g in gears if isinstance(g, SingleGear))
    compounds_count = sum(1 for g in gears if isinstance(g, CompoundGear))

    print()
    print(f"  ╔{'═' * 54}╗")
    print(f"  ║{'Spur Gear Solver':^54}║")
    print(f"  ╠{'═' * 54}╣")
    W = 54
    inv_str = f"{singles_count} single, {compounds_count} compound gear(s)"

    def box_line(text: str) -> str:
        return f"  ║  {text:<{W - 4}}║"

    print(box_line(f"Target ratio  :  {args.ratio:.4f}"))
    print(box_line(f"Inventory     :  {inv_str}"))
    print(box_line(f"Max stages    :  {args.max_stages}"))
    print(f"  ╚{'═' * 54}╝")
    print()

    solutions = solve(gears, args.ratio, max_stages=args.max_stages, top_n=args.top)

    if not solutions:
        print("  No valid gear combinations found.")
        print("  Try adding more gears or increasing --max-stages.")
        sys.exit(0)

    print(f"  Top {len(solutions)} solution(s):")
    print()

    for i, sol in enumerate(solutions, 1):
        _print_solution(i, sol, args.ratio)


if __name__ == "__main__":
    main()
