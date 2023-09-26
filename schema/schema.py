
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
    