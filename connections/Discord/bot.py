"""A thin, opt-in Discord client for the CaesarOS API. No intelligence lives here."""
import asyncio
import os
from pathlib import Path

import discord
import httpx
from dotenv import load_dotenv

from caesaros.state.workflow_state import TERMINAL


def create_client():
    load_dotenv(Path(__file__).resolve().parents[2] / '.env')
    owner_id = os.getenv('DISCORD_OWNER_ID', '')
    channel_id = os.getenv('DISCORD_CHANNEL_ID', '')
    if not owner_id.isdigit() or not channel_id.isdigit():
        raise ValueError('Set DISCORD_OWNER_ID and DISCORD_CHANNEL_ID to your numeric Discord IDs.')
    base_url = os.getenv('CAESAROS_API_URL', 'http://127.0.0.1:8000').rstrip('/')
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print('CaesarOS Discord client ready; using the configured personal channel.')

    @client.event
    async def on_message(message):
        if message.author.bot or message.author.id != int(owner_id) or message.channel.id != int(channel_id):
            return
        if not message.content.startswith('!caesar '):
            return
        prompt = message.content[len('!caesar '):].strip()
        if not prompt:
            return
        async with message.channel.typing():
            try:
                async with httpx.AsyncClient(base_url=base_url, timeout=20) as api:
                    response = await api.post('/api/runs', json={'user_input': prompt})
                    response.raise_for_status()
                    state = response.json()
                    for _ in range(240):
                        response = await api.get('/api/runs/' + state['id'])
                        response.raise_for_status()
                        state = response.json()
                        if state['workflow_status'] in TERMINAL:
                            break
                        await asyncio.sleep(1)
                    reply = state['final_response'] or state['error'] or 'Still running. Inspect the workflow in Agents Mode.'
                    if state['proposed_actions']:
                        reply += '\n\nReview calendar approvals in the local Agents Mode dashboard.'
                    for start in range(0, len(reply), 1800):
                        await message.channel.send(reply[start:start + 1800], allowed_mentions=discord.AllowedMentions.none())
            except httpx.HTTPError:
                await message.channel.send('CaesarOS could not be reached. Check the backend and API URL.')
    return client


if __name__ == '__main__':
    client = create_client()
    token = os.getenv('BOT_TOKEN')
    if not token:
        raise ValueError('Set BOT_TOKEN in .env before starting Discord.')
    client.run(token)
