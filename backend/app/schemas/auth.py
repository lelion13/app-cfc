from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=10, max_length=512)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class BootstrapStatusOut(BaseModel):
    allowed: bool


class BootstrapRequest(BaseModel):
    username: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=10, max_length=512)
    setup_token: str = Field(min_length=8, max_length=512)
