"""
main.py
-------
Mini-PyPSA Main Application.
Load any grid data file directly in code, solve power flows,
print terminal results, and show the white-background graph.
"""

import os
from network.loader import load_network_from_json
from analysis.solver import PowerFlowSolver
from visualization.plots import plot_network


# ---------------------------------------------------------------------------
# SET YOUR INPUT FILE HERE:
# Available example files in data/:
#   - "data/balanced_grid.json"        (Balanced: Demand = Supply)
#   - "data/line_overload.json"        (Line Congestion > 100%)
#   - "data/demand_not_supplied.json"  (Power Shortage / Deficit)
#   - "data/five_generators_grid.json" (5 Diverse Generators + Battery)
# ---------------------------------------------------------------------------
INPUT_FILE = "data/demand_not_supplied.json"


def print_results(results: dict, network_name: str) -> None:
    """Print clean, formatted power system results to the terminal."""
    balance = results["balance"]

    print("\n" + "=" * 55)
    print(f"      RESULTS: {network_name.upper()}")
    print("=" * 55)

    print("\n--- Power Balance ---")
    print(f"Total Generation : {balance['generation']:.1f} MW")
    print(f"Storage Support  : {balance['storage']:.1f} MW")
    print(f"Total Demand     : {balance['demand']:.1f} MW")
    print(f"Unserved Demand  : {balance['unserved']:.1f} MW")
    
    if balance["unserved"] > 1e-4:
        print("Grid Status      : [!] DEFICIT - DEMAND NOT FULLY SUPPLIED")
    else:
        print("Grid Status      : [OK] BALANCED")

    print("\n--- Generator Dispatch (Merit-Order) ---")
    for name, mw in results["dispatch"].items():
        print(f"  {name:<18}: {mw:>6.1f} MW")

    print("\n--- Transmission Line Flows ---")
    overloaded_found = False
    for line in results["lines"]:
        tag = f"[{line['status']}]"
        if line["status"] == "OVERLOADED":
            overloaded_found = True
        print(
            f"  {line['name']:<15}: {line['flow']:>6.1f} / {line['capacity']:<4.0f} MW "
            f"({line['loading_percent']:>5.1f}%) {tag}"
        )
    if overloaded_found:
        print("  --> WARNING: One or more transmission lines are overloaded!")

    print(f"\nOperating Cost   : Rs. {results['cost']:.2f}/hour")
    print("=" * 55 + "\n")


def main():
    # 1. Resolve path relative to this file
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, INPUT_FILE)

    print(f"Loading grid model from: {file_path}")

    # 2. File Handling: Load network from JSON
    grid = load_network_from_json(file_path)

    # 3. Solve economic dispatch & power flow
    solver = PowerFlowSolver(grid)
    results = solver.solve()

    # 4. Print results to terminal
    print_results(results, grid.name)

    # 5. Display single-line diagram on white background
    plot_network(grid)


if __name__ == "__main__":
    main()
