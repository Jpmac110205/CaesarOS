from copy import deepcopy
from langgraph.graph import END, START, StateGraph
from caesaros.decision.router import WORKFLOWS, route
from caesaros.state.workflow_state import WorkflowState


def build_graph(ctx):
    """Agents read/write state; conditional graph edges own their execution order."""
    async def decide(original):
        state = deepcopy(original)
        decision = route(state['user_input'], state['requested_workflow'])
        state.update(decision=decision, selected_workflow=decision['workflow'], intent=decision['workflow'],
                     workflow_status='running', current_agent='router')
        state['confidence_scores']['routing'] = decision['confidence']
        state['agent_sequence'] = WORKFLOWS.get(decision['workflow'], [])
        ctx.event(state, 'router', f"{decision['gate'].capitalize()} · {decision['reason']}")
        ctx.save(state)
        await ctx.pause()
        return state

    async def escalate(original):
        state = deepcopy(original)
        state['current_agent'] = 'reasoning'
        ctx.event(state, 'reasoning', 'Escalating a medium-confidence routing decision.')
        ctx.save(state)
        workflow, reason = await ctx.reasoner.escalate(state)
        state.update(selected_workflow=workflow, intent=workflow, agent_sequence=WORKFLOWS.get(workflow, []))
        state['decision']['escalation'] = reason
        if not workflow:
            state['decision']['gate'] = 'clarify'
        ctx.event(state, 'reasoning', reason)
        ctx.save(state)
        return state

    def after_router(state):
        return 'escalate' if state['decision']['gate'] == 'escalate' else next_node(state)

    def next_node(state):
        if state['decision']['gate'] == 'clarify' or state['cursor'] >= len(state['agent_sequence']):
            return 'respond'
        return state['agent_sequence'][state['cursor']]

    graph = StateGraph(WorkflowState)
    graph.add_node('router', decide)
    graph.add_node('escalate', escalate)
    graph.add_node('respond', ctx.respond)
    graph.add_edge(START, 'router')
    destinations = {name: name for name in ['escalate', 'respond', 'planner', 'email', 'tutor', 'fitness', 'code']}
    graph.add_conditional_edges('router', after_router, destinations)
    graph.add_conditional_edges('escalate', next_node, destinations)
    for name in ['planner', 'email', 'tutor', 'fitness', 'code']:
        graph.add_node(name, ctx.agent_node(name))
        graph.add_conditional_edges(name, next_node, destinations)
    graph.add_edge('respond', END)
    return graph.compile()
