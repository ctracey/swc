# Tech Debt

## [3.2] — F-05: hash IDs ambiguous with pure-digit number refs — 2026-05-18

**Severity:** info
**Location:** `cli/swc_workload.py:243-256` (`find_by_ref`)
**Description:** `find_by_ref` classifies a ref as a number via `re.fullmatch(r"\d+(?:\.\d+)*", ref)`. Hash IDs are 7 hex chars; one in ~16^7 (~6 per 100M) will be all-digit and so be misclassified as a number reference. If it ever happens the user sees a confusing "not found" or, worse, silently acts on a different item that happens to occupy that number.
**Accepted because:** Probability is vanishing. Park as a curiosity. Possible future hardening: when a numeric-looking ref doesn't resolve as a number but matches an all-digit hash, fall through to ID lookup; or require hash refs to be prefixed (e.g. `@abc123d`).

## [3.2] — F-06: cli/swc_workload.py approaching breakup threshold — 2026-05-18

**Severity:** info
**Location:** `cli/swc_workload.py` (whole file, 938 lines)
**Description:** Single module combines persistence, tree manipulation, rendering, status logic, and argparse wiring. Over the 500-line guideline. Each section is already comment-divided so a split into `persistence.py`, `tree.py`, `render.py`, `commands.py`, `cli.py` is mechanical.
**Accepted because:** Defer until 3.3 adds material (plugin wrapper, hook integration, complete-flag op). Splitting now would be premature; splitting at 3.3 lands naturally with the new code.
