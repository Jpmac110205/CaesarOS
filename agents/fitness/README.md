# Fitness Agent

Fitness combines the Planner's free-time calculation with normalized BeneFIT training context.

`tools.py` obtains the current goal, recent workout, weekly frequency, next workout, duration, and exercise list through `DemoServices.fitness()`. `agent.py` reads `planner_output.available_blocks`, searches for a sufficiently long evening gap, and writes `fitness_output`.

If a workout fits, the output includes its exact start, end, duration, exercises, weekly progress, and goal. If no uninterrupted block is available, it says so and produces no calendar proposal. Fitness does not modify Planner state or book an event itself.

The workout workflow therefore looks like:

```text
Planner → planner_output.available_blocks
Fitness → fitness_output.workout
Response builder → proposed calendar action
User approval → deterministic calendar executor
```

The sample recommendation is scheduling assistance, not medical advice or a claim about real health data. `prompt.md` prevents the live reasoning provider from inventing recovery or nutrition measurements.

To connect BeneFIT, implement the adapter in `caesaros/services/catalog.py`. Firebase credentials and database access should remain behind BeneFIT's own authenticated API.

