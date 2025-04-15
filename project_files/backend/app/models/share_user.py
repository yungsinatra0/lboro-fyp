from sqlmodel import SQLModel

class UserShare(SQLModel):
    name: str
    dob: str | None = None