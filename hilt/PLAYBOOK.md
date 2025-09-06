HILT Playbook - Safe steps

1. Always branch from `master` (create `feature/human-in-loop-tests`).
2. Keep experiments in `hilt/` and avoid modifying core `backend/` or `frontend/` code unless necessary.
3. Use descriptive commits and small atomic changes. Include test updates.
4. Tag milestones (e.g., v1.0.1-hilt-alpha) for reproducibility.
5. Run backend tests before merging to `master`.
6. Do not commit large model files or secrets. Use `.gitignore` and environment variables.
7. Document dataset sources and random seeds in `hilt/config.yml`.
