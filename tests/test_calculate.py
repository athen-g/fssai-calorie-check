import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("calculate", ROOT / "scripts" / "calculate.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class EnergyTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "examples" / "yogabar.json").read_text())

    def test_yogabar_both_interpretations_and_serving(self):
        result = MODULE.calculate(self.data)
        self.assertFalse(result["carbohydrate_basis_confirmed_by_input"])
        inc, exc = result["scenarios"]
        self.assertAlmostEqual(inc["calculated_kcal"], 364.1)
        self.assertAlmostEqual(exc["calculated_kcal"], 408.5)
        self.assertAlmostEqual(inc["portion_calculated_kcal"], 182.05)
        self.assertEqual(result["portion_from_label_kcal"], 182)

    def test_explicit_available_carbohydrate(self):
        self.data.update(carbohydrate_g=46.2, carbohydrate_basis="excludes_fibre")
        self.assertAlmostEqual(MODULE.calculate(self.data)["scenarios"][0]["calculated_kcal"], 364.1)

    def test_special_sources_no_double_count(self):
        self.data.update(protein_g=0, fat_g=0, carbohydrate_g=30, fibre_g=5,
                         carbohydrate_basis="includes_fibre", other_energy_sources="specified",
                         polyols_g=10, erythritol_g=5, ethanol_g=2, organic_acids_g=1,
                         carbohydrate_includes_polyols=True)
        # 10g ordinary carbs + 5g fibre + 10g polyol + 5g erythritol + ethanol + acid.
        self.assertEqual(MODULE.calculate(self.data)["scenarios"][0]["calculated_kcal"], 87)

    def test_reject_bad_values(self):
        for value in (-1, float("nan"), float("inf"), True, "26", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                MODULE.calculate(dict(self.data, protein_g=value))

    def test_missing_fibre_is_not_zero(self):
        del self.data["fibre_g"]
        with self.assertRaises(ValueError):
            MODULE.calculate(self.data)

    def test_reject_impossible_explicit_carbohydrate(self):
        self.data.update(carbohydrate_g=2, carbohydrate_basis="includes_fibre")
        with self.assertRaises(ValueError):
            MODULE.calculate(self.data)

    def test_unknown_basis_preserves_possible_scenario(self):
        self.data["carbohydrate_g"] = 2
        result = MODULE.calculate(self.data)
        self.assertIn("error", result["scenarios"][0])
        self.assertIn("calculated_kcal", result["scenarios"][1])

    def test_special_fields_require_explicit_mode(self):
        self.data["polyols_g"] = 10
        with self.assertRaises(ValueError):
            MODULE.calculate(self.data)

    def test_missing_special_overlap_rejected(self):
        self.data.update(other_energy_sources="specified", polyols_g=0,
                         erythritol_g=0, ethanol_g=0, organic_acids_g=0)
        with self.assertRaises(ValueError):
            MODULE.calculate(self.data)


if __name__ == "__main__":
    unittest.main()
