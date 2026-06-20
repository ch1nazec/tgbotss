from datetime import date, time
from pydantic import BaseModel, ConfigDict


class RecordingRequest(BaseModel):
    id: int

    user_id: int
    master_id: int
    day_booking: date
    time_booking: time


class UserModel(BaseModel):
    id: int
    
    telegram_id: int

    last_name: str
    first_name: str
    third_name: str | None = None
    date_birth: date

    model_config = ConfigDict(from_attributes=True)


class MasterModel(BaseModel):
    id: int
    
    user_id: int
    stage: int


class FeedbackModel(BaseModel):
    id: int
    
    rating: int
    description: str


class PhotoFeedbackModel(BaseModel):
    id: int
    
    photo: str
    feedback_id: int

    model_config = ConfigDict(from_attributes=True)






# Create models
class UserCreate(BaseModel):
    telegram_id: int

    last_name: str
    first_name: str
    third_name: str | None = None

    date_birth: date

class RecordingRequestCreate(BaseModel):
    user_id: int
    master_id: int
    day_booking: date
    time_booking: time


class MasterCreate(BaseModel):
    user_id: int
    stage: int


class FeedbackCreate(BaseModel):
    rating: int
    description: str


class PhotoFeedbackCreate(BaseModel):
    photo: str
    feedback_id: int

    model_config = ConfigDict(from_attributes=True)





class UserUpdate(BaseModel):
    last_name: str
    first_name: str
    third_name: str | None = None

    date_birth: date