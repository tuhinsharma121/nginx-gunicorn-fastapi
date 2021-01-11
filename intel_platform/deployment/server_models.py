from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class Container(BaseModel):
    container_id: str = None
    message: str = None


class Request(BaseModel):
    name: str = None
    company: str = None



class BaseUser(BaseModel):
    user_id: str
    company_name: str
    full_name: str
    disabled: bool


class NewUser(BaseUser):
    password: str


class RegisteredUser(BaseUser):
    hashed_password: str


class Client(BaseModel):
    user_id: str
    company_name: str
    full_name: str
    disabled: bool

class ResponseMessage(BaseModel):
    status: str = None
    message: str = None