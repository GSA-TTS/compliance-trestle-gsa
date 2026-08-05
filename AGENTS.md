# AGENTS.md

`compliance-trestle-gsa` is a plugin for [compliance-trestle](https://github.com/oscal-compass/compliance-trestle) that validates and scaffolds GSA IT SSPs (OSCAL SystemSecurityPlan models). It ships subcommands under the `trestle` CLI, not a standalone binary.

## Commands
- Setup: `make develop` (installs `-e .[dev]`). Requires Python >= 3.11.
- Test: `make test` (`pytest -vvvv --exitfirst -n auto` — stops on first failure, runs parallel via pytest-xdist).
- Single test: `python -m pytest tests/trestle_gsa/commands/validate_test.py::test_valid_ssp`.
- Lint: `make code-lint` (`flake8`, max line length 120). CI order is test then lint; both must pass.
- Build/release: `make package` / `make release` (twine).

## Plugin wiring (non-obvious)
- Trestle discovers this plugin by the top-level package name starting with `trestle_` (see trestle's `core/plugins.py`). The importable package is `trestle_gsa` (under `src/`), NOT `compliance_trestle_gsa`. Do not rename it.
- Command classes are auto-collected from the `trestle_gsa/commands/` submodule; each is a `CommandPlusDocs` subclass with a `name` attr. Adding a new file there with such a class registers a new `trestle <name>` subcommand — there are no `entry_points` to update.
- Plugin discovery does NOT run in trestle's own unit tests, so this repo's tests invoke command classes directly (`ValidateCmd()._run(args)`) rather than through the `trestle` CLI.

## Subcommands
- `trestle gsa-validate -f path/to/ssp.json` — works on merged or split models.
- `trestle gsa-defaults -f path/to/ssp.json` — adds boilerplate `REPLACE_ME` defaults; **merged models only** (rejects split/decomposed dirs).
- `trestle tag-revision -f <metadata.json> -c <changes>` — prepends a revision entry; **merged models only**. Undocumented in README.

## Conventions / gotchas
- Models subclass trestle's OSCAL types and use **pydantic v1** APIs imported as `from pydantic.v1 import ...`. Do not use pydantic v2 syntax; trestle pins to the v1 shim.
- Validation logic lives in `src/trestle_gsa/core/` (`gsa.py` orchestrates, `metadata.py` and `system_characteristics.py` define required-field constraints). `gsa-defaults` fills these via `generators.generate_sample_model` + `deep_merge` (`core/merge.py`, which dedupes lists by `id`/`role_id`).
- Required-field rules (minimum role IDs, XAL props, responsible parties, diagram links) are enforced by pydantic `@validator`s — change constraints there, and keep test fixtures in `tests/resources/` (`valid-gsa-ssp.json` must pass, `valid-base-ssp.json` must fail validation) in sync.
- Tests bootstrap a real trestle project: `tmp_trestle_dir` fixture runs `trestle init` and imports fixtures by monkeypatching `sys.argv`. When testing CLI-driven flows, follow that pattern in `tests/conftest.py`.
