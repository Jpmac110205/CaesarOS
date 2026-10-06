# External clients and future connectors

This folder contains interface/client code and placeholders for integrations that live outside the CaesarOS core package.

- `Discord/` is a working thin client of the CaesarOS API.
- `Google/`, `Prodigy/`, and `BeneFIT/` document future integration responsibilities.

The executable service adapters currently live in `caesaros/services/`, because agents should access every provider through one consistent application boundary. These folders are useful for provider-specific OAuth callbacks, SDK setup, deployment notes, or companion-client code when those pieces become large enough to stand alone.

No connector should contain orchestration logic. It should authenticate, translate provider data into a documented normalized contract, handle provider-specific errors, and return control to CaesarOS.

