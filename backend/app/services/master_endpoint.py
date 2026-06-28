from datetime import date

from fastapi import APIRouter, HTTPException, Depends
from api.schemas import MasterModel
from api.common_schema import ResultResponse

from api.dao import MasterDAO, UserDAO, RecordingDAO

from dao.sessionmake_fastapi import DatabaseSession

from utils.helpers import response_wrapper_result

from sqlalchemy.ext.asyncio import AsyncSession


master_router = APIRouter(prefix='/master')


@master_router.get('/available-slots/{master_id}')
async def master_available_slots(
            master_id: int,
            session: AsyncSession = Depends(DatabaseSession.get_db
    )):
    check_master = await MasterDAO.find_one_or_none_id(id=master_id, session=session)
    if not check_master:
        raise HTTPException(status_code=404, detail='Хуебесы не нашли такого мастера :(')
    
    book_available = await RecordingDAO.get_available_slots(session=session, master_id=master_id, start_date=date.today())
    return book_available


@master_router.post('/add/{user_id}', response_model=ResultResponse[MasterModel])
async def make_user_to_master(
    user_id: int,
    session: AsyncSession = Depends(DatabaseSession.get_db_with_commit
                                        )):
    check_user = await UserDAO.find_one_or_none_id(session=session, id=user_id)
    if not check_user:
        raise HTTPException(status_code=404, detail=f'Хуебесы не смогли найти юзера по {user_id}')

    new_master = await MasterDAO.user_to_master(session=session, user_id=user_id)
    return response_wrapper_result(result=MasterModel.model_validate(new_master))