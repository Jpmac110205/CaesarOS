from caesaros.decision.relevance import filter_documents

async def retrieve(state, ctx, query):
    if not state['memory_context']:
        state['memory_context'] = await ctx.tool(state, 'memory.retrieve', ctx.services.memory)
    candidates = await ctx.tool(state, 'prodigy.retrieve', lambda: ctx.services.documents(query))
    docs = await filter_documents(state, ctx.jev, query, candidates)
    state['retrieved_documents'] = docs
    for doc in docs:
        if not any(s['id'] == doc['id'] for s in state['sources']):
            state['sources'].append({'id': doc['id'], 'title': doc['title'], 'source': doc['source'], 'relevance': doc['relevance']})
    return docs
