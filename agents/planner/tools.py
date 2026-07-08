#TOOLS: Email agent, Weather, News, Google Calendar, Google Tasks, Workout Agent
import os

import pyowm

def get_weather(location: str) -> str:
    """
    Fetches the current weather for a given location using the OpenWeatherMap API.
    """
    try:
        owm = pyowm.OWM('YOUR_API_KEY')  # Replace with your actual API key
        mgr = owm.weather_manager()
        observation = mgr.weather_at_place(location)
        weather = observation.weather
        return f"The current weather in {location} is {weather.detailed_status} with a temperature of {weather.temperature('celsius')['temp']}°C."
    except Exception as e:
        return f"Error fetching weather data: {str(e)}"

#Have to figure out how to get the news. Maybe an API will do
def get_news() -> str:
    """
    Fetches the latest news headlines. This is a placeholder function and should be implemented with an actual news API.
    """
    # Placeholder implementation
    return "Here are the latest news headlines: [News Headline 1], [News Headline 2], [News Headline 3]."


## Must integrate Google APIs in connections folder for actual functionality first
def get_calendar_events() -> str:
    """
    Fetches upcoming events from the user's Google Calendar. This is a placeholder function and should be implemented with actual Google Calendar API integration.
    """
    # Placeholder implementation
    return "Here are your upcoming calendar events: [Event 1], [Event 2], [Event 3]."

def get_tasks() -> str:
    """
    Fetches tasks from the user's Google Tasks. This is a placeholder function and should be implemented with actual Google Tasks API integration.
    """
    # Placeholder implementation
    return "Here are your tasks: [Task 1], [Task 2], [Task 3]."

def load_agent_prompt(filename: str = "prompt.md") -> str:
    """
    Standard utility helper (Not an LLM tool). 
    Loads the system markdown file from disk before the LLM call 
    to keep context windows lightweight.
    """
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error loading planner prompt file: {str(e)}"