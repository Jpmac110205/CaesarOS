from agents.email.tools import load_context
from caesaros.services.model_outputs import EmailResult


async def run(state, ctx):
    await load_context(state, ctx)
    classifications = await ctx.jev.classify_emails(state)
    by_id = {item['id']: item for item in classifications}
    important = sorted((e for e in state['emails'] if by_id[e['id']]['priority'] == 'high'),
                       key=lambda e: e.get('deadline') or '')
    interview = next((e for e in important if by_id[e['id']]['category'] == 'interview'), None)
    generated = await ctx.reasoner.generate('email', state, EmailResult,
        'Summarize the inbox using Jev classifications and the actual message contents. '
        'Generate a context-specific reply draft when useful, otherwise draft must be null. '
        'Do not invent the recipient identity or commit to attendance without user confirmation. Never send mail.',
        classifications=classifications, important_emails=important, interview=interview)
    state['email_output'] = {**generated, 'important_emails': important,
        'classifications': classifications, 'interview': interview, 'draft_status': 'Draft only · never sent'}
