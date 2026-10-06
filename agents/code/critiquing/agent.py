def critique(proposal, testing):
    return {'status': 'reviewed', 'notes': ['Keep credentials in service adapters.',
            'Use shared state rather than direct agent calls.', 'Run the generated test cases before using an artifact.']}
