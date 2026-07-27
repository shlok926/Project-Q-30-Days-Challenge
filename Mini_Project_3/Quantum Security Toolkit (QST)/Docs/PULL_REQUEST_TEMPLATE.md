## Description

What does this PR do? Link any related issue.

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update (`docs/` and/or `specs/`)
- [ ] Refactor (no behavior change)
- [ ] Other (please describe)

## Self-Review Checklist

Per `docs/16_CODING_STANDARDS.md` §10 — please confirm each item:

- [ ] This change keeps `core/` free of `visualization/`/`cli/` imports (dependency rules — `docs/07_SYSTEM_ARCHITECTURE.md` §7).
- [ ] All new public functions are documented (Google-style docstrings — `docs/16_CODING_STANDARDS.md` §9).
- [ ] If this touches `BB84Protocol` or `Eavesdropper`, the regression tests in `docs/11_SECURITY_ARCHITECTURE.md` §4 / `docs/14_TESTING_STRATEGY.md` §3 have been run and still pass.
- [ ] New dependencies are pinned and justified (`docs/06_TECHNICAL_REQUIREMENTS.md` §10).
- [ ] Test coverage for changed code meets the relevant target in `docs/14_TESTING_STRATEGY.md` §12.
- [ ] Relevant `docs/`/`specs/` files are updated to match this change — **or** I've confirmed below that none need updating.
- [ ] No new `TODO`/shortcut was introduced without logging it in `docs/15_ROADMAP.md` §8 Technical Debt Backlog.

## Documentation Impact

- [ ] I updated the following document(s): _____________________
- [ ] No documentation impact — this is an internal-only change, because: _____________________

## Testing

Describe how this was tested. Include any relevant seed values used for reproducibility (per `specs/SIMULATION_SPEC.md` §6 Determinism Contract), so a reviewer can reproduce your results exactly.

## Additional Notes

Anything else a reviewer should know.
