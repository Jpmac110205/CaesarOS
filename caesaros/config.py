import os
from dataclasses import dataclass, field
from pathlib import Path
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    database: Path = ROOT / '.data' / 'caesaros.sqlite3'
    timezone: str = 'America/New_York'
    reasoner: str = field(default='openai', init=False)
    api_key: str = field(default='', repr=False)
    openai_model: str = 'gpt-4.1-mini'
    jev_api_key: str = field(default='', repr=False)
    jev_model: str = 'typesafe/jev-1.13'
    step_delay: float = 0

    @classmethod
    def from_env(cls):
        load_dotenv(ROOT / '.env')
        timezone = os.getenv('CAESAROS_TIMEZONE', 'America/New_York')
        ZoneInfo(timezone)
        settings = cls(database=Path(os.getenv('CAESAROS_DATABASE', str(cls.database))),
                       timezone=timezone,
                       api_key=os.getenv('OPENAI_API_KEY') or os.getenv('OpenAI_API_KEY', ''),
                       openai_model=os.getenv('CAESAROS_OPENAI_MODEL', cls.openai_model),
                       jev_api_key=os.getenv('JEV_API_KEY') or os.getenv('Jev_API_KEY') or os.getenv('OPENROUTER_API_KEY', ''),
                       jev_model=os.getenv('CAESAROS_JEV_MODEL', cls.jev_model),
                       step_delay=max(0, float(os.getenv('CAESAROS_STEP_DELAY', '0'))))
        settings.validate()
        return settings

    def validate(self):
        ZoneInfo(self.timezone)
        if not self.api_key:
            raise ValueError('Set OPENAI_API_KEY (or OpenAI_API_KEY) in .env')
        if not self.jev_api_key:
            raise ValueError('Set JEV_API_KEY (or Jev_API_KEY / OPENROUTER_API_KEY) to your OpenRouter key in .env')
        if not self.openai_model or not self.jev_model:
            raise ValueError('OpenAI and Jev model IDs must not be empty')
