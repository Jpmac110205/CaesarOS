import discord
import os
from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()

# Set up clients
intents = discord.Intents.default()
intents.message_content = True  # Required to read messages
client = discord.Client(intents=intents)

openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Conversation memory (in-memory, resets when bot restarts)
conversation_history = [
    {"role": "system", "content": "You are a helpful, friendly assistant chatting on Discord whose name is Caesar."}
]

MAX_HISTORY_MESSAGES = 20  # keep last 20 messages (not counting system prompt) to control cost/context length

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    global conversation_history

    # Ignore the bot's own messages to avoid infinite loops
    if message.author == client.user:
        return

    prompt = message.content.strip()
    if not prompt:
        return

    # Add the user's message to history
    conversation_history.append({"role": "user", "content": prompt})

    # Trim history (keep system prompt + last N messages)
    if len(conversation_history) > MAX_HISTORY_MESSAGES + 1:
        conversation_history = [conversation_history[0]] + conversation_history[-MAX_HISTORY_MESSAGES:]

    async with message.channel.typing():
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=conversation_history
            )
            reply = response.choices[0].message.content

            # Add the assistant's reply to history so it remembers what it said
            conversation_history.append({"role": "assistant", "content": reply})

            await message.channel.send(reply)
        except Exception as e:
            await message.channel.send(f"Error talking to OpenAI: {e}")

client.run(os.getenv('BOT_TOKEN'))