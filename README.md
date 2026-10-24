# FSSAI calorie check

An AI skill for checking the arithmetic on Indian food labels. Give your assistant a clear nutrition-label photo or a table of nutrient values. It checks the serving basis, calculates energy and explains the assumptions.

The skill handles the main trap in the Yoga Bar example: carbohydrate may include fibre. Adding fibre calories without checking this can count fibre twice. When the definition is unclear, the skill shows both interpretations.

## Use the skill

Copy this repository's folder into your assistant's skills directory under the name `fssai-calorie-check`. For Codex, the usual destination is `~/.codex/skills/fssai-calorie-check`. Follow your assistant's instructions for refreshing skills.

Example request:

> Use $fssai-calorie-check to check this nutrition label. Show the fibre assumption and calculate calories for a 50 g portion.

The skill uses the standard `SKILL.md` format. It requires an assistant that can read that format; image reading depends on the host assistant. The optional arithmetic helper needs Python 3.9 or later and uses only the standard library.

## Run the example

```sh
python scripts/calculate.py examples/yogabar.json
python -m unittest discover -s tests -v
```

For the supplied Yoga Bar values, the helper returns 364.1 kcal per 100 g if carbohydrate includes fibre, and 408.5 kcal if it excludes fibre. The printed value is 364 kcal. The close match suggests that fibre is included, but the label does not explicitly confirm that definition.

The example is transcribed from screenshots supplied during development. It is not a laboratory result or a claim that a current website or every batch has the same composition. No packaging images are bundled.

See [calculation notes](references/calculation.md) for the input fields, formulas and official source links. The bundled source baseline was reviewed on 24 October 2026; check later FSSAI amendments before relying on regulatory statements.

## Writing

The instructions use plain language and preserve equations, units and uncertainty. They were reviewed using the Avoid AI Writing rules in a documentation context. That writing skill is optional at runtime and is not bundled here. This project makes no claim about bypassing AI detectors.

## Limits

A matching calorie calculation establishes arithmetic consistency under stated assumptions. It does not verify the food's composition, certify FSSAI compliance or determine whether a food is suitable for someone's diet.
