import os
from dataclasses import dataclass
from pathlib import Path
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    database: Path = ROOT / '.data' / 'caesaros.sqlite3'
    timezone: str = 'America/New_York'
    reasoner: str = 'demo'
    api_key: str = ''
    claude_model: str = ''
    step_delay: float = 0.35

    @classmethod
    def from_env(cls):
        load_dotenv(ROOT / '.env')
        mode = os.getenv('CAESAROS_REASONER', 'demo')
        if mode not in {'demo', 'claude'}:
            raise ValueError('CAESAROS_REASONER must be demo or claude')
        timezone = os.getenv('CAESAROS_TIMEZONE', 'America/New_York')
        ZoneInfo(timezone)
        settings = cls(database=Path(os.getenv('CAESAROS_DATABASE', str(cls.database))),
                       timezone=timezone, reasoner=mode,
                       api_key=os.getenv('ANTHROPIC_API_KEY', ''),
                       claude_model=os.getenv('CAESAROS_CLAUDE_MODEL', ''),
                       step_delay=max(0, float(os.getenv('CAESAROS_STEP_DELAY', '.35'))))
        if mode == 'claude' and not (settings.api_key and settings.claude_model):
            raise ValueError('Claude mode requires ANTHROPIC_API_KEY and CAESAROS_CLAUDE_MODEL')
        return settings
