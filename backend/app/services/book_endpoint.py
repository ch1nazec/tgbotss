from loguru import logger

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from api.schemas import RecordingRequest, RecordingRequestCreate

from api.dao import RecordingDAO, UserDAO

from sqlalchemy.ext.asyncio import AsyncSession
from dao.sessionmake_fastapi import DatabaseSession

from api.common_schema import ResultResponse


book_router = APIRouter(prefix='/book')


@book_router.post('/')
async def book_appointment(
    book: RecordingRequestCreate,
    session: AsyncSession = Depends(DatabaseSession.get_db_with_commit)):
    today_date = datetime.today().date()

    if today_date > book.day_booking:
        logger.warning(book.time_booking.hour)
        raise HTTPException(
            status_code=400,
            detail='Хуебесы не могут задним числом вас записать на запись :(')
    elif today_date == book.day_booking:
        if datetime.now().hour > book.time_booking.hour:
            raise HTTPException(
            status_code=400,
            detail='Хуебесы не могут задним часом вас записать на запись :(')

    booking = await RecordingDAO.book_appointment(
            session=session,
            master_id=book.master_id,
            user_id=book.user_id,
            date_book=book.day_booking,
            time_book=book.time_booking
        )
    master_info = await UserDAO.find_one_or_none_id(id=booking.master.user_id, session=session)
    
    appointment_detail = {
            'id': booking.id,
            'date_book': booking.day_booking.strftime(f'%Y-%m-%d'),
            'time_book': booking.time_booking.strftime('%H:%M'),

            'user_id': booking.user_id,
            'master_id': booking.master_id,

            'master_full_name': f'{master_info.last_name} {master_info.first_name} {master_info.third_name}'
    }
    return {
            'status': 'SUCCESS',
            'message': 'Запись успешно создана',
            'appointment': appointment_detail
        }


@book_router.get('/{user_id}', response_model=list[RecordingRequest])
async def get_booking_user(
    user_id: int,
    session: AsyncSession = Depends(DatabaseSession.get_db)):

    booking_of_users = await UserDAO.get_booking_user(session=session, user_id=user_id)
    if not booking_of_users:
        raise HTTPException(status_code=404, detail='Пользователь не найден.')
    return booking_of_users