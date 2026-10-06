# Critiquing stage

The critique stage reviews the coding proposal and its generated test checklist. It currently emphasizes service boundaries, credential placement, shared-state communication, and the need to run tests before trusting an artifact.

Its structured notes become `code_output.critiquing_output`. The stage has no direct tools and makes no repository changes. In a future repair loop, this output could be sent back to the coding stage with a strict iteration limit, but that loop is not implemented in the local demo.

