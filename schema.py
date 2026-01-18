from pydantic import BaseModel
from typing import List, Tuple

class QuestionModel(BaseModel):
    q: str
    answers: List[Tuple[str, int]] # List of [Answer, Points]

class GameData(BaseModel):
    team_names: List[str]
    questions: List[QuestionModel]