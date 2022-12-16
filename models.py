from pydantic import BaseModel

class User(BaseModel):
    name: str
    username: str
    password: str

class Login(BaseModel):
    username: str
    password: str