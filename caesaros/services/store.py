import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from caesaros.services.fixtures import seed_data


class Store:
    """SQLite transactions protect approvals and isolate concurrent workflows."""
    def __init__(self, path: Path, timezone: str):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path, self.timezone = path, timezone
        with self.connect() as db:
            db.execute('PRAGMA journal_mode=WAL')
            db.executescript('''
                CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, created TEXT, body TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS data (id INTEGER PRIMARY KEY CHECK(id=1), body TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS schedules (id TEXT PRIMARY KEY, body TEXT NOT NULL);
            ''')
            db.execute('INSERT OR IGNORE INTO data VALUES (1, ?)', (json.dumps(seed_data(timezone)),))
            for name, hour, prompt in [
                ('morning_digest', 8, 'Prepare my morning digest.'),
                ('afternoon_checkin', 14, 'Check my progress and adjust my remaining priorities.'),
                ('evening_review', 21, 'Review my day and prepare tomorrow’s priorities.')]:
                item = {'id': name, 'hour': hour, 'minute': 0, 'enabled': False, 'prompt': prompt, 'last_run_id': None}
                db.execute('INSERT OR IGNORE INTO schedules VALUES (?, ?)', (name, json.dumps(item)))

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        try:
            with db:
                yield db
        finally:
            db.close()

    def save_run(self, state):
        state['revision'] += 1
        with self.connect() as db:
            db.execute('INSERT INTO runs VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET body=excluded.body',
                       (state['id'], state['created_at'], json.dumps(state)))

    def run(self, run_id):
        with self.connect() as db:
            row = db.execute('SELECT body FROM runs WHERE id=?', (run_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def runs(self, limit=50):
        with self.connect() as db:
            rows = db.execute('SELECT body FROM runs ORDER BY created DESC LIMIT ?', (limit,)).fetchall()
        return [json.loads(row[0]) for row in rows]

    def data(self):
        with self.connect() as db:
            return json.loads(db.execute('SELECT body FROM data WHERE id=1').fetchone()[0])

    def update_data(self, transform):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            data = json.loads(db.execute('SELECT body FROM data WHERE id=1').fetchone()[0])
            result = transform(data)
            db.execute('UPDATE data SET body=? WHERE id=1', (json.dumps(data),))
        return result

    def schedules(self):
        with self.connect() as db:
            return [json.loads(row[0]) for row in db.execute('SELECT body FROM schedules ORDER BY id')]

    def save_schedule(self, item):
        with self.connect() as db:
            db.execute('UPDATE schedules SET body=? WHERE id=?', (json.dumps(item), item['id']))

    def approve(self, run_id, action_id, decision):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT body FROM runs WHERE id=?', (run_id,)).fetchone()
            if not row:
                raise KeyError('Workflow not found')
            state = json.loads(row[0])
            action = next((a for a in state['proposed_actions'] if a['id'] == action_id), None)
            if not action:
                raise KeyError('Action not found')
            if action['status'] != 'pending':
                if action['status'] == ('approved' if decision == 'approve' else 'rejected'):
                    return state
                raise ValueError('This action has already been resolved')
            if state['workflow_status'] != 'awaiting_approval':
                raise ValueError('This workflow is not awaiting approval')
            if decision == 'approve':
                data = json.loads(db.execute('SELECT body FROM data WHERE id=1').fetchone()[0])
                if action['type'] != 'calendar.create':
                    raise ValueError('Unsupported action type')
                event = action['payload']
                start, end = datetime.fromisoformat(event['start']), datetime.fromisoformat(event['end'])
                if end <= start:
                    raise ValueError('Event must have positive duration')
                if any(start < datetime.fromisoformat(e['end']) and end > datetime.fromisoformat(e['start']) for e in data['calendar_events']):
                    raise ValueError('Calendar changed: this time overlaps another event. Run a new workflow.')
                data['calendar_events'].append({**event, 'id': action_id, 'source': 'Demo Calendar · approved'})
                db.execute('UPDATE data SET body=? WHERE id=1', (json.dumps(data),))
            action['status'] = 'approved' if decision == 'approve' else 'rejected'
            state['events'].append({'at': datetime.now().astimezone().isoformat(), 'node': 'execution',
                                    'message': f"{action['status'].capitalize()}: {action['title']} (local demo calendar)"})
            if all(a['status'] != 'pending' for a in state['proposed_actions']):
                state['workflow_status'] = 'completed'
            state['revision'] += 1
            db.execute('UPDATE runs SET body=? WHERE id=?', (json.dumps(state), run_id))
        return state
