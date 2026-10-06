"""HTTP and accounting shared by live providers. No offline response path."""
import httpx


class ProviderResponseError(ValueError):
    """The provider refused, truncated, or returned an invalid result."""


async def post_json(url, key, payload):
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(url, headers={'Authorization': f'Bearer {key}'}, json=payload)
        response.raise_for_status()
        body = response.json()
    if not isinstance(body, dict) or body.get('error'):
        raise ProviderResponseError('Provider returned an error response')
    return body


def record_usage(state, provider, body):
    usage = body.get('usage') or {}
    metrics = state['metrics']
    metrics['model_calls'] += 1
    for name in ('input_tokens', 'output_tokens'):
        metrics[name] += usage.get(name, 0)
    # Record actual provider/model/usage without credentials or raw response bodies.
    metrics.setdefault('provider_calls', []).append({
        'provider': provider, 'model': body.get('model'), 'response_id': body.get('id'),
        'input_tokens': usage.get('input_tokens', 0), 'output_tokens': usage.get('output_tokens', 0),
        **({'cost_usd': usage['cost']} if 'cost' in usage else {})})
