"""Synthetic data, generated relative to the local date. No network access."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def seed_data(timezone: str) -> dict:
    today = datetime.now(ZoneInfo(timezone)).replace(hour=0, minute=0, second=0, microsecond=0)
    def at(hour, minute=0, days=0):
        return (today + timedelta(days=days, hours=hour, minutes=minute)).isoformat()
    return {
        'date': today.date().isoformat(),
        'calendar_events': [
            {'id': 'class-os', 'title': 'Operating Systems', 'start': at(10), 'end': at(11, 15), 'source': 'Demo Calendar'},
            {'id': 'lab', 'title': 'Physics lab', 'start': at(13), 'end': at(14, 30), 'source': 'Demo Calendar'},
            {'id': 'project-sync', 'title': 'Project sync', 'start': at(16), 'end': at(17), 'source': 'Demo Calendar'},
            {'id': 'dinner', 'title': 'Dinner & reset', 'start': at(18, 30), 'end': at(19), 'source': 'Demo Calendar'}],
        'tasks': [
            {'id': 'physics', 'title': 'Physics problem set', 'due': at(23, 59, 1), 'priority': 1, 'minutes': 60, 'completed': False},
            {'id': 'interview', 'title': 'Practice interview algorithms', 'due': at(12, 0, 2), 'priority': 2, 'minutes': 45, 'completed': False},
            {'id': 'caesaros', 'title': 'Build CaesarOS service adapters', 'due': at(18, 0, 3), 'priority': 3, 'minutes': 40, 'completed': False}],
        'emails': [
            {'id': 'recruiter', 'sender': 'Alex · Example Labs', 'subject': 'Software engineering interview',
             'body': 'Your technical interview is in two days at noon. Please confirm attendance. Prepare arrays, hash maps, and sliding window problems.',
             'category': 'interview', 'action_required': True, 'deadline': at(12, 0, 2)},
            {'id': 'course', 'sender': 'Physics course team', 'subject': 'Exam preparation materials',
             'body': 'Review forces, work and energy before the exam. Your problem set is due tomorrow.',
             'category': 'coursework', 'action_required': True, 'deadline': at(23, 59, 1)},
            {'id': 'newsletter', 'sender': 'Developer Weekly', 'subject': 'This week in engineering',
             'body': 'Weekly articles and community updates.', 'category': 'newsletter', 'action_required': False, 'deadline': None}],
        'documents': [
            {'id': 'physics-forces', 'title': 'Physics · Forces & Newton’s laws', 'tags': ['physics', 'forces', 'newton', 'exam'],
             'content': 'Draw a free-body diagram. Resolve forces into components. Apply ΣF = ma separately on each axis. Weight is mg; normal force depends on contact geometry. A balanced net force means zero acceleration.', 'source': 'Demo Prodigy / Physics notes'},
            {'id': 'physics-energy', 'title': 'Physics · Work & energy', 'tags': ['physics', 'energy', 'work', 'exam'],
             'content': 'For constant force, W = Fd cos θ. The work-energy theorem is W_net = ΔK, with K = ½mv². Mechanical energy is conserved when only conservative forces do work.', 'source': 'Demo Prodigy / Physics notes'},
            {'id': 'os-memory', 'title': 'Operating Systems · Virtual memory', 'tags': ['virtual memory', 'paging', 'page fault', 'operating systems', 'os'],
             'content': 'Virtual memory gives each process an isolated virtual address space. A page table maps virtual pages to physical frames. The TLB caches translations. A page fault transfers control to the OS when a mapping is absent or access is invalid; the OS may load a page or terminate an invalid access.', 'source': 'Demo Prodigy / OS notes'},
            {'id': 'os-kernel', 'title': 'Operating Systems · The kernel', 'tags': ['kernel', 'operating systems', 'os'],
             'content': 'The kernel manages CPU scheduling, memory, devices and system calls. User programs request privileged operations through system calls, which cross the user/kernel boundary.', 'source': 'Demo Prodigy / OS notes'},
            {'id': 'algorithms', 'title': 'Interview guide · Sliding window', 'tags': ['interview', 'algorithm', 'sliding window', 'code'],
             'content': 'Maintain left and right indices over a contiguous window. Expand right, track counts in a hash map, and shrink left while the constraint is violated. Each pointer advances at most n times, yielding O(n) time.', 'source': 'Demo Prodigy / Interview guide'}],
        'fitness': {'goal': 'Train consistently three times per week', 'weekly_sessions': 2,
                    'last_workout': {'name': 'Upper body', 'date': (today - timedelta(days=2)).date().isoformat()},
                    'next_workout': 'Lower body', 'duration_minutes': 75,
                    'exercises': [{'name': 'Warm-up', 'sets': '10 min'}, {'name': 'Squat', 'sets': '3 × 8'},
                                  {'name': 'Romanian deadlift', 'sets': '3 × 10'}, {'name': 'Split squat', 'sets': '3 × 8 / side'},
                                  {'name': 'Cool-down', 'sets': '5 min'}]},
        'github': {'repository': 'CaesarOS (sample context)', 'branch': 'demo',
                   'summary': 'FastAPI backend with LangGraph, shared workflow state and service adapters.',
                   'open_items': ['Implement service adapters', 'Add routing evaluation', 'Embed Agents Mode in Prodigy']},
        'memory': [{'id': 'preferences', 'content': 'Prefer workouts after 5 PM and study in the evening. Keep 10 minutes between focus blocks.', 'source': 'Demo Prodigy / Preferences'}],
        'notifications': []}
