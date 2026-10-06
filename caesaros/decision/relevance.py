import re


def filter_documents(query, documents):
    """Deterministic relevance stand-in with visible scores and source IDs."""
    q, ranked = query.lower(), []
    tokens = set(re.findall(r'\w+', q))
    for doc in documents:
        matches = sum(tag.lower() in q if ' ' in tag else tag.lower() in tokens for tag in doc['tags'])
        if matches:
            ranked.append({**doc, 'relevance': round(min(.99, .65 + .1 * matches), 2)})
    return sorted(ranked, key=lambda d: d['relevance'], reverse=True)[:3]
