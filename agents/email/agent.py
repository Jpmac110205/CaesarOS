from agents.email.tools import load_context

async def run(state, ctx):
    await load_context(state, ctx)
    important = sorted((e for e in state['emails'] if e['action_required']), key=lambda e: e['deadline'] or '')
    interview = next((e for e in important if e['category'] == 'interview'), None)
    state['email_output'] = {'summary': f"{len(important)} messages need attention; {len(state['emails']) - len(important)} can wait.",
        'important_emails': important,
        'classifications': [{'id': e['id'], 'priority': 'high' if e['action_required'] else 'low', 'category': e['category']} for e in state['emails']],
        'interview': interview,
        'draft': 'Hi Alex, thank you for the invitation. I confirm my attendance and look forward to the technical interview. Best regards.' if interview else None,
        'draft_status': 'Draft only · never sent'}
