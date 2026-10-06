def review(proposal):
    # Demo checks are a checklist; user code is never executed.
    return {'status': 'checklist_generated', 'executed': False,
            'cases': ['Empty input', 'Repeated values', 'All unique values', 'Invalid service response', 'Transient adapter failure']}
