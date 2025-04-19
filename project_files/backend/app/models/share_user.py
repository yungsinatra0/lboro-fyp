from sqlmodel import SQLModel

# User share model used when creating share links, is separate to the main User models to avoid circular import issues
class UserShare(SQLModel):
    name: str
    dob: str | None = None