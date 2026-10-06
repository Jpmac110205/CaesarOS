# Testing stage

`await review(state, ctx, proposal)` asks OpenAI to inspect the actual coding proposal and generate specific test cases, validated as `TestReview`. Python sets `executed: false`; these are proposed tests, not passing test results. The repository's pytest suite is separate.
