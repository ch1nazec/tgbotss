from fastapi import APIRouter, Depends, HTTPException, status

from api.schemas import UserCreate, UserModel, UserUpdate
from api.common_schema import ResultResponse

from api.dao import UserDAO

from utils.helpers import response_wrapper_result

from sqlalchemy.ext.asyncio import AsyncSession
from dao.sessionmake_fastapi import DatabaseSession


user_router = APIRouter(prefix='/users')


@user_router.post('', response_model=ResultResponse[UserModel])
async def get_current_or_create_user(user_data: UserCreate,
                                     session: AsyncSession = Depends(DatabaseSession.get_db_with_commit)):
    db_user = await UserDAO.create_or_get(session, user_data)
    pydantic_user = UserModel.model_validate(db_user)

    return response_wrapper_result(result=pydantic_user)


@user_router.get('/{user_id}', response_model=ResultResponse[UserModel])
async def get_user(user_id: int, session: AsyncSession = Depends(DatabaseSession.get_db)):
    db_user = await UserDAO.find_one_or_none_id(id=user_id, session=session)
    pydantic_user = UserModel.model_validate(db_user)

    return response_wrapper_result(result=pydantic_user)


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