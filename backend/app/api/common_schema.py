from pydantic import BaseModel
from typing import Generic, TypeVar 


M = TypeVar('M', bound=BaseModel)

class ResultResponse(BaseModel, Generic[M]):
    result: M