def propose(state):
    interview = state['selected_workflow'] == 'interview'
    sender = (state['email_output'].get('interview') or {}).get('sender', '') if interview else ''
    return {'title': 'Technical interview practice · ' + sender if interview else 'CaesarOS implementation plan',
        'steps': ['Review arrays and hash maps (20 min)', 'Solve a sliding window problem (35 min)', 'Explain complexity and test edge cases (20 min)', 'Rehearse a project walkthrough (15 min)'] if interview else
                 ['Define typed service contracts', 'Implement one authenticated read-only adapter', 'Normalize data at the service boundary', 'Add failure and retry tests before enabling writes'],
        'artifact': "def longest_unique(text: str) -> int:\n    seen, left, best = {}, 0, 0\n    for right, char in enumerate(text):\n        if char in seen and seen[char] >= left:\n            left = seen[char] + 1\n        seen[char] = right\n        best = max(best, right - left + 1)\n    return best" if interview else None}
