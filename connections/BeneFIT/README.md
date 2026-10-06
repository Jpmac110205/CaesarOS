# BeneFIT integration placeholder

BeneFIT remains the fitness application and owner of its Firebase data. CaesarOS should call an authenticated BeneFIT API instead of accessing Firebase directly.

The normalized training-context contract currently includes:

- fitness goal and sessions completed this week;
- last workout name and date;
- next planned workout and expected duration;
- exercise names and prescribed sets or time.

The Fitness Agent combines this context with Planner availability. It should not diagnose health conditions or infer measurements absent from BeneFIT.

Implement authentication, authorization, Firebase access, and data aggregation inside BeneFIT. Replace `DemoServices.fitness()` with an HTTP adapter that returns the same shape and clearly distinguishes unavailable data from zero values. See `docs/INTEGRATIONS.md` for the remaining work.

