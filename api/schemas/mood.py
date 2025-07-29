from pydantic import BaseModel

class MoodBase(BaseModel):
    name: str
    description: str | None = None
    image_url: str | None = None

class MoodCreate(MoodBase):
    pass

class Mood(MoodBase):
    id: int

    class Config:
        orm_mode = True