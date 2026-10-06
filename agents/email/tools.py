async def load_context(state, ctx):
    emails = await ctx.tool(state, 'email.list', ctx.services.emails)
    # Old local databases may still contain preassigned demo classifications.
    state['emails'] = [{k: v for k, v in email.items() if k not in {'category', 'action_required'}} for email in emails]
