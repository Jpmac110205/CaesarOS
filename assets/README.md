# Compatibility state imports

This folder exists for compatibility with the original project shell.

- `agentstate.py` re-exports the current `WorkflowState` type and `new_state` factory from `caesaros/state/`.
- `codestate.py` defines the small typed structure used to describe the Code Agent's three internal stages.

The original shell stored values as mutable class attributes, which allowed data to leak between requests. The working demo allocates a new dictionary for every workflow and persists independent snapshots in SQLite. New code should import from `caesaros.state` directly; these files let older imports continue working during migration.

