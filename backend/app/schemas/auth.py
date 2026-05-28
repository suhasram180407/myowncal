from pydantic import BaseModel, EmailStr, validator


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

    @validator("password")
    def password_max_bytes(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password too long: must be 72 bytes or fewer")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
