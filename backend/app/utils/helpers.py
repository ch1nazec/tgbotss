from functools import wraps

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


ALLOWED_EXTENSIONS = {'image/jpeg', 'image/png', 'image/webp'}
UPLOAD_DIR = 'static/images'

def response_wrapper_result(result, status_code=status.HTTP_200_OK):
    response = {"result": jsonable_encoder(result)}
    
    return JSONResponse(content=response, status_code=status_code)


