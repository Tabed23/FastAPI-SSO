
from enum import Enum

from pydantic import BaseModel


class Role(Enum):
    user = "user"
    admin = "admin"
    
    
class User(BaseModel):
    first_name  : str
    last_name : str
    password : str
    email : str
    

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


