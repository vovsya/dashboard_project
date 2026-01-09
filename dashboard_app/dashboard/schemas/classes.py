from pydantic import BaseModel, SecretStr, Field
from enum import Enum

class UserData(BaseModel):
    username: str = Field(min_length=4, max_length=16)
    password: SecretStr = Field(min_length=8, max_length=64)

class Token(BaseModel):
    access_token: str
    token_type: str

class WidgetChoice(str, Enum):
    nickname    = "Добавить ваш ник"
    weather     = "Добавить погоду"
    time        = "Добавить время"
    date        = "Добавить дату"
    traffic     = "Добавить пробки"

class Choice(str, Enum):
    add     = "Добавить виджет"
    delete  = "Удалить виджет"
