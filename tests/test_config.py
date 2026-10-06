import pytest
from caesaros.config import Settings

KEY_NAMES = ['OPENAI_API_KEY', 'OpenAI_API_KEY', 'JEV_API_KEY', 'Jev_API_KEY', 'OPENROUTER_API_KEY']


@pytest.fixture
def isolated_env(tmp_path, monkeypatch):
    monkeypatch.setattr('caesaros.config.ROOT', tmp_path)
    for name in KEY_NAMES + ['CAESAROS_OPENAI_MODEL', 'CAESAROS_JEV_MODEL', 'CAESAROS_REASONER']:
        monkeypatch.delenv(name, raising=False)
    return tmp_path


@pytest.mark.parametrize('openai_name,jev_name', [
    ('OPENAI_API_KEY', 'JEV_API_KEY'),
    ('OpenAI_API_KEY', 'Jev_API_KEY'),
    ('OPENAI_API_KEY', 'OPENROUTER_API_KEY'),
])
def test_env_file_key_aliases_and_live_defaults(isolated_env, openai_name, jev_name):
    (isolated_env / '.env').write_text(f'{openai_name}=openai-secret\n{jev_name}=router-secret\nCAESAROS_REASONER=demo\n')
    settings = Settings.from_env()
    assert settings.api_key == 'openai-secret' and settings.jev_api_key == 'router-secret'
    assert settings.reasoner == 'openai' and settings.openai_model == 'gpt-4.1-mini'
    assert settings.jev_model == 'typesafe/jev-1.13'
    assert 'openai-secret' not in repr(settings) and 'router-secret' not in repr(settings)


def test_missing_keys_fail_instead_of_selecting_demo(isolated_env):
    with pytest.raises(ValueError, match='OPENAI_API_KEY'):
        Settings.from_env()
    (isolated_env / '.env').write_text('OPENAI_API_KEY=test-key\n')
    with pytest.raises(ValueError, match='JEV_API_KEY'):
        Settings.from_env()


def test_process_env_takes_precedence(isolated_env, monkeypatch):
    (isolated_env / '.env').write_text('OPENAI_API_KEY=file-key\nJEV_API_KEY=router-key\n')
    monkeypatch.setenv('OPENAI_API_KEY', 'process-key')
    assert Settings.from_env().api_key == 'process-key'
