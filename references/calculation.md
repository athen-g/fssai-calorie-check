# Calculation notes

## Sources and scope

Source review date: 24 October 2026.

- [FSSAI Labelling and Display Regulations, Version VIII, 9 September 2025](https://fssai.gov.in/upload/uploadfiles/files/Comp_Labelling%20Display_Version%20VIII_09_09_2025.pdf), regulation 5(3)(e)(i), printed page 13: energy conversion factors.
- [FAO, Methods of food analysis](https://www.fao.org/4/y5022e/y5022e03.htm): total carbohydrate includes fibre; available carbohydrate excludes it.
- [Codex nutrition-labelling guidance hosted by FSSAI](https://www.fssai.gov.in/upload/uploadfiles/files/Guidelines_Nutrition_Labelling_16_08_2018.pdf), section 3.2.1: available carbohydrate excludes dietary fibre. This is Codex guidance, not a substitute for Indian law.
- [FSSAI amendment index](https://www.fssai.gov.in/food-law/regulations/amendments/labelling-display): check for later amendments and their effective dates when discussing current requirements.

These sources establish the factors and the distinction between carbohydrate definitions. They do not establish which definition a particular manufacturer's label uses.

## Energy factors

| Component | kcal/g |
|---|---:|
| Available carbohydrate | 4 |
| Protein | 4 |
| Fat | 9 |
| Dietary fibre | 2 |
| Polyols other than erythritol | 2 |
| Erythritol | 0 |
| Ethanol | 7 |
| Organic acids | 3 |

Let C be the printed carbohydrate, P protein, F fat, DF fibre, Q non-erythritol polyols, R erythritol, A ethanol and O organic acids, all in grams on the same basis.

First derive ordinary available carbohydrate U from C by subtracting only components known to be included in C:

`U = C - included_DF - included_Q - included_R`

Then calculate:

`E = 4*U + 4*P + 9*F + 2*DF + 2*Q + 0*R + 7*A + 3*O`

Alcohol and organic acids must also be separate from C for this helper. If a carbohydrate-by-difference result includes either, resolve and remove that overlap before calculating. Reject negative U; do not force it to zero.

An ingredient list alone cannot supply the gram quantities of special ingredients. If polyols, FOS or other fermentable ingredients are relevant, establish how they were measured and classified. Do not count a fibre ingredient twice, infer its quantity from ingredient order, or assign all non-sugar sweeteners the polyol factor. When the necessary quantities are unavailable, give a conditional estimate and identify the gap.

## Calculator input

Pass one JSON object. Required fields: `protein_g`, `carbohydrate_g`, `fat_g`, `fibre_g`, `carbohydrate_basis` (`includes_fibre`, `excludes_fibre`, or `unknown`), `basis_quantity`, `basis_unit` (`g` or `ml`), and `other_energy_sources` (`none` or `specified`). The caller must establish whether other sources matter; the helper does not inspect ingredient lists.

Optional fields: `label_kcal`, `portion_quantity`, `product`, `source_note`. With `specified`, all five fields `polyols_g`, `erythritol_g`, `ethanol_g`, `organic_acids_g` and `carbohydrate_includes_polyols` (boolean) are required. The boolean applies to both polyol categories. Resolve mixed inclusion manually before using the helper.

Use explicit zeros only for quantities known to be zero or deliberately assumed absent. Record assumptions in `source_note` and carry them into the explanation. Nonfinite, negative, missing and mistyped values are rejected. Unknown fibre inclusion produces both scenarios; unknown special-ingredient overlap must be resolved before invoking the helper.

The helper reports signed difference as calculated minus printed energy. It does not classify legal compliance or decide how much difference rounding permits. Per-serving rounding can differ slightly from scaling unrounded per-100-g values. Keep full precision during the calculation and round only the displayed answer.

## Yoga Bar example

The supplied screenshot declares per 100 g: protein 26 g, carbohydrate 57.3 g, fat 5.9 g, fibre 11.1 g and energy 364 kcal. The carbohydrate definition is not explicit.

Including fibre in carbohydrate gives `(57.3-11.1)*4 + 26*4 + 5.9*9 + 11.1*2 = 364.1 kcal`. Excluding fibre gives `408.5 kcal`. The former reconciles after rounding, so inclusion is a supported inference. The screenshot's 50 g dry serving declares 182 kcal; its milk-prepared column declares 364 kcal. Keep those servings separate.
