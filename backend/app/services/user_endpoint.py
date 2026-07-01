import hmac, hashlib, json
from urllib.parse import parse_qsl
from fastapi import APIRouter, Depends, HTTPException, status, Header


from api.schemas import UserCreate, UserModel, UserUpdate
from api.common_schema import ResultResponse
# from verification_bot import get_current_telegram_user
from api.dao import UserDAO

from utils.helpers import response_wrapper_result

from sqlalchemy.ext.asyncio import AsyncSession
from dao.sessionmake_fastapi import DatabaseSession

from config import bot_token


user_router = APIRouter(prefix='/users')

def get_current_telegram_user(
        authorization: str = Header(None)):
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Missing or invalid Auth headers structure')
    
    init_data_raw = authorization.replace('Bearer ', '').strip()
    parsed_data = dict(parse_qsl(init_data_raw))

    if 'hash' not in parsed_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Error Telegram payload: missing hash parameter')
    
    received_hash = parsed_data.pop('hash')
    data_check_string = '\n'.join(f'{k}={v}' for k, v in sorted(parsed_data.items()))

    secret_key = hmac.new(b'WebAppData', bot_token.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authorization failed: Data verification mismatch'
        )
    return parsed_data


@user_router.post('', response_model=ResultResponse[UserModel])
async def get_current_or_create_user(user_data: UserCreate,
                                     session: AsyncSession = Depends(DatabaseSession.get_db_with_commit)):
    db_user = await UserDAO.create_or_get(session=session, user_data=user_data)
    pydantic_user = UserModel.model_validate(db_user)

    return response_wrapper_result(result=pydantic_user)


@user_router.get('/{user_id}',)
async def get_user(user_id: int, session: AsyncSession = Depends(DatabaseSession.get_db)):
    db_user = await UserDAO.find_one_or_none_id(id=user_id, session=session)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Хуебесы не нашли такого юзера')
    pydantic_user = UserModel.model_validate(db_user)

    return pydantic_user.model_dump(exclude_defaults=True)


@user_router.patch('/change/{user_id}', response_model=UserUpdate)
async def update_user(user_id: int,
                      item_update: UserUpdate,
                      session: AsyncSession = Depends(DatabaseSession.get_db_with_commit)):
    updated_user = await UserDAO.update_for_id(
                                session=session,
                                new_value=item_update,
                                record_id=user_id)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Юзер не найден.')
    return updated_user


@user_router.post('/auth/verify')
def verify_user(
    tg_data: dict = Depends(get_current_telegram_user)):
    user_json = tg_data.get("user")
    if not user_json:
        raise HTTPException(status_code=400, detail="User object missing from data")
        
    user_info = json.loads(user_json)
    return {
        "status": "success",
        "telegram_id": user_info.get("id"),
        "username": user_info.get("username"),
        "first_name": user_info.get("first_name"),
        'last_name': user_info.get('last_name'),
        'photo': user_info.get('photo_url')
    }