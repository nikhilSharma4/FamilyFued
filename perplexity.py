import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from schema import GameData

load_dotenv()

def generate_game_content(user_topic):
    client = OpenAI(
        api_key=os.getenv("PERPLEXITY_API_KEY"),
        base_url="https://api.perplexity.ai"
    )

    prompt = f"""
    Create a Family Feud game about: {user_topic}.
    
    Requirements:
    1. Generate 2 creative team names.
    2. Generate exactly 10 questions.
    3. Each question MUST have exactly 8 answers.
    4. Points for each question must sum up to 100.
    5. Return ONLY a JSON object that follows the schema.
    """

    response = client.chat.completions.create(
        model="sonar-reasoning-pro",
        messages=[
            {"role": "system", "content": "You are a professional game show writer. Output only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )

    # Parse and validate with Pydantic
    content = response.choices[0].message.content
    data_dict = json.loads(content)
    return GameData(**data_dict)