# \# implement.md

# 

# \## Source of truth

# Use AGENTS.md and project\_spec.md as the primary instructions.

# 

# \## Delivery approach

# Single-agent implementation only.

# 

# \## Milestones

# 1\. Scaffold repo structure

# 2\. Add pyproject.toml, requirements.txt, README.md

# 3\. Define shared schemas and abstract provider interfaces

# 4\. Build normalization layer

# 5\. Build revenue analysis module

# 6\. Build profitability module

# 7\. Build return-ratio module

# 8\. Build balance-sheet module

# 9\. Build cash-flow module

# 10\. Build valuation module

# 11\. Build red-flag module

# 12\. Build scoring module

# 13\. Build thesis builder

# 14\. Build charts and report generator

# 15\. Build run\_analysis.py orchestration entry point

# 16\. Add tests and fix failures

# 17\. Update documentation.md

# 

# \## Execution rules

# \- Keep diffs scoped to the current milestone.

# \- Do not implement transcript or filing parsing in MVP.

# \- Do not add vendor-specific API dependencies yet.

# \- Use provider-agnostic interfaces.

# \- Use pathlib for all file paths.

# \- Add tests for any metric-computing module.

# \- Run validation after each milestone and fix failures before moving on.

# \- Update documentation.md continuously.

# 

# \## Validation checklist

# \- pytest

# \- import checks

# \- smoke test for run\_analysis.py

# \- path handling works with Windows paths

# \- outputs written under outputs/

# 

# \## Suggested order of coding

# 1\. repo skeleton

# 2\. schemas and provider interfaces

# 3\. normalized dataframe contract

# 4\. financial modules

# 5\. reporting

# 6\. orchestration

# 7\. tests and cleanup

# 

# \## Notes

# \- Keep formulas explicit and easy to audit.

# \- Prefer annual financial data only for MVP.

# \- Handle missing columns gracefully and log warnings when appropriate.

