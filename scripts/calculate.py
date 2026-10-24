"""Calculate conditional food-label energy; Python standard library only."""

import argparse
import json
import math
from decimal import Decimal
from pathlib import Path


def number(data, key, positive=False):
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        raise ValueError(f"{key} must be a number")
    if not math.isfinite(value) or value < 0 or (positive and value == 0):
        raise ValueError(f"{key} must be finite and {'positive' if positive else 'nonnegative'}")
    return Decimal(str(value))


def calculate(data):
    if not isinstance(data, dict):
        raise ValueError("Input must be a JSON object")
    p, c, f, df = [number(data, key) for key in
                   ("protein_g", "carbohydrate_g", "fat_g", "fibre_g")]
    basis = data.get("carbohydrate_basis")
    if basis not in ("includes_fibre", "excludes_fibre", "unknown"):
        raise ValueError("Set carbohydrate_basis to includes_fibre, excludes_fibre or unknown")
    quantity = number(data, "basis_quantity", positive=True)
    unit = data.get("basis_unit")
    if unit not in ("g", "ml"):
        raise ValueError("basis_unit must be g or ml")
    mode = data.get("other_energy_sources")
    special_keys = ("polyols_g", "erythritol_g", "ethanol_g", "organic_acids_g")
    if mode == "specified":
        q, r, a, o = [number(data, key) for key in special_keys]
        includes_polyols = data.get("carbohydrate_includes_polyols")
        if not isinstance(includes_polyols, bool):
            raise ValueError("carbohydrate_includes_polyols must be a boolean")
    elif mode == "none":
        if any(key in data for key in (*special_keys, "carbohydrate_includes_polyols")):
            raise ValueError("Use specified when supplying special-source fields")
        q = r = a = o = Decimal(0)
        includes_polyols = False
    else:
        raise ValueError("Set other_energy_sources to none or specified")
    label = number(data, "label_kcal") if "label_kcal" in data else None
    portion = number(data, "portion_quantity", positive=True) if "portion_quantity" in data else None
    choices = ("includes_fibre", "excludes_fibre") if basis == "unknown" else (basis,)
    scenarios = []
    for choice in choices:
        available = c - (df if choice == "includes_fibre" else 0)
        if includes_polyols:
            available -= q + r
        if available < 0:
            if basis == "unknown":
                scenarios.append({"carbohydrate_basis": choice,
                                  "error": "Included components exceed carbohydrate"})
                continue
            raise ValueError("Included components exceed carbohydrate")
        components = {"available_carbohydrate": 4 * available,
                      "protein": 4 * p, "fat": 9 * f, "fibre": 2 * df,
                      "polyols": 2 * q, "erythritol": 0 * r,
                      "ethanol": 7 * a, "organic_acids": 3 * o}
        energy = sum(components.values())
        item = {"carbohydrate_basis": choice,
                "available_carbohydrate_g": float(available),
                "components_kcal": {k: float(v) for k, v in components.items()},
                "calculated_kcal": float(energy)}
        if label is not None:
            item["calculated_minus_label_kcal"] = float(energy - label)
        if portion is not None:
            item["portion_calculated_kcal"] = float(energy * portion / quantity)
        scenarios.append(item)
    result = {"product": data.get("product"), "source_note": data.get("source_note"),
              "basis_quantity": float(quantity), "basis_unit": unit,
              "carbohydrate_basis_confirmed_by_input": basis != "unknown",
              "scenarios": scenarios}
    if label is not None:
        result["label_kcal"] = float(label)
    if portion is not None:
        result["portion_quantity"] = float(portion)
        if label is not None:
            result["portion_from_label_kcal"] = float(label * portion / quantity)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Nutrition values as JSON")
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8-sig"), parse_float=Decimal)
        print(json.dumps(calculate(data), indent=2, ensure_ascii=True))
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(2, f"Input error: {exc}\n")


if __name__ == "__main__":
    main()
