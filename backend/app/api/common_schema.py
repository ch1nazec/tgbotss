from pydantic import BaseModel
from typing import Generic, TypeVar 


M = TypeVar('M', BaseModel)

class ResultResponse(BaseModel, Generic[M]):
    result: M