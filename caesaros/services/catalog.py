from datetime import datetime, timedelta
from caesaros.services.store import Store


class DemoServices:
    """Replace adapters here; agents never access raw external APIs."""
    def __init__(self, store: Store):
        self.store = store

    def calendar(self):
        # TODO(GOOGLE): OAuth read-only calendar adapter; normalize timezone-aware events.
        return self.store.data()['calendar_events']

    def tasks(self):
        # TODO(GOOGLE): Google Tasks adapter with completion state and deadlines.
        return self.store.data()['tasks']

    def emails(self):
        # TODO(GMAIL): Fetch messages with least-privilege OAuth; strip unsafe markup.
        return self.store.data()['emails']

    def documents(self, query):
        # TODO(PRODIGY): Call your retrieval API, returning IDs, content and citations.
        return self.store.data()['documents']

    def memory(self):
        # TODO(PRODIGY): Retrieve user-scoped preferences and long-term context.
        return self.store.data()['memory']

    def fitness(self):
        # TODO(BENEFIT): Call BeneFIT's authenticated API; keep Firebase behind BeneFIT.
        return self.store.data()['fitness']

    def github(self):
        # TODO(GITHUB): Read repository metadata using a fine-grained read-only token.
        return self.store.data()['github']

    def review_memory(self, run_id, content):
        def update(data):
            if not any(m['id'] == run_id for m in data['memory']):
                data['memory'].append({'id': run_id, 'content': content, 'source': 'Demo memory / Evening review'})
        self.store.update_data(update)

    def notify(self, run_id, content):
        # TODO(NOTIFICATIONS): Add Discord/Prodigy delivery and deduplicate by run ID.
        def update(data):
            if not any(n['run_id'] == run_id for n in data['notifications']):
                data['notifications'].append({'run_id': run_id, 'content': content})
                data['notifications'] = data['notifications'][-100:]
        self.store.update_data(update)


def available_blocks(events, start: datetime, end: datetime) -> list[dict]:
    """Merge busy intervals and calculate actual gaps, including overlapping events."""
    cursor, result = start, []
    for event in sorted(events, key=lambda e: e['start']):
        busy_start, busy_end = datetime.fromisoformat(event['start']), datetime.fromisoformat(event['end'])
        if busy_end <= start or busy_start >= end:
            continue
        if busy_start > cursor:
            result.append(block(cursor, min(busy_start, end)))
        cursor = max(cursor, busy_end)
        if cursor >= end:
            break
    if cursor < end:
        result.append(block(cursor, end))
    return result


def block(start, end, title='Available time'):
    return {'title': title, 'start': start.isoformat(), 'end': end.isoformat(),
            'minutes': int((end - start).total_seconds() / 60)}


def reserve(blocks, minutes, title, earliest_hour=0):
    """Consume a gap so subsequent agents cannot propose overlapping work."""
    for i, gap in enumerate(blocks):
        start, end = datetime.fromisoformat(gap['start']), datetime.fromisoformat(gap['end'])
        start = max(start, start.replace(hour=earliest_hour, minute=0))
        finish = start + timedelta(minutes=minutes)
        if finish <= end:
            replacement = []
            original_start = datetime.fromisoformat(gap['start'])
            if start > original_start:
                replacement.append(block(original_start, start))
            if finish + timedelta(minutes=10) < end:
                replacement.append(block(finish + timedelta(minutes=10), end))
            blocks[i:i + 1] = replacement
            return block(start, finish, title)
    return None
