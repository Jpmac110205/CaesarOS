#TOOLS: get daily nutrient goals, get workouts, get food data, calculate protein status, calendar agent

import os


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
        return f"Error loading fitness prompt file: {str(e)}"

def get_daily_nutrient_goals() -> str:
    """
    Fetches the user's daily nutrient goals. This is a placeholder function and should be implemented with actual logic to retrieve user-specific data.
    """
    # Placeholder implementation
    return "Your daily nutrient goals are: Protein: 150g, Carbohydrates: 250g, Fats: 70g."

def get_workouts() -> str:
    """
    Fetches the user's workout plan. This is a placeholder function and should be implemented with actual logic to retrieve user-specific workout data.
    """
    # Placeholder implementation
    return "Your upcoming workouts are: [Workout 1], [Workout 2], [Workout 3]."

def get_food_data(food_item: str) -> str:
    """
    Fetches nutritional information for a given food item. This is a placeholder function and should be implemented with actual logic to retrieve food data.
    """
    # Placeholder implementation
    return f"Nutritional information for {food_item}: Calories: 200, Protein: 10g, Carbohydrates: 30g, Fats: 5g."

def calculate_protein_status(current_protein_intake: float, daily_protein_goal: float) -> str:
    """
    Calculates the user's protein status based on current intake and daily goal.
    """
    if current_protein_intake >= daily_protein_goal:
        return "You have met or exceeded your daily protein goal."
    else:
        remaining = daily_protein_goal - current_protein_intake
        return f"You need {remaining}g more protein to meet your daily goal."

