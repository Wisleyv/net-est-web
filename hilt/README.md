Human-in-the-Loop Testing (HILT)

This directory holds non-breaking scaffolding and configuration for human-in-the-loop
validation runs (Portuguese → Portuguese). Keep all experimental scripts and heavy
models off `master`; develop and test in `feature/human-in-loop-tests` instead.

Files:
- config.yml: initial configuration for HILT runs (models, timeouts, data paths)
- PLAYBOOK.md: recommended steps to run HILT experiments safely

Do not add production secrets or large model files here. Use remote model stores and
local `.env` files if needed.
