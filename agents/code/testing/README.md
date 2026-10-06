# Testing stage

This stage converts the coding proposal into a validation checklist. It currently returns representative cases such as empty input, repeated values, invalid service responses, and transient failures.

`executed: false` is intentional and important. The demo has no sandbox for arbitrary generated programs, so this stage must never represent generated cases as passing tests. The repository's real CaesarOS test suite is separate under `/tests` and is executed with pytest.

The parent Code Agent stores this result in `code_output.testing_output` and passes it to the critique stage. A future execution implementation should run in an isolated service with resource limits and return command, exit status, logs, and artifact hashes.

