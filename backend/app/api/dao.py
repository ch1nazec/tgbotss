from datetime import date, timedelta, datetime, time
from fastapi import HTTPException
from loguru import logger

from sqlalchemy import select, and_, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.base import BaseDAO
from app.dao.models import User, Recording, Master, Feedback, PhotoFeedback


class UserDAO(BaseDAO[User]):
    model = User


class MasterDAO(BaseDAO[Master]):
    model = Master


class RecordingDAO(BaseDAO[Recording]):
    model = Recording

    
    @classmethod
    def generate_working_hours(cls, start_hour=10, end_hour=20, step_hours=2) -> list[str]:
        working_hours = []
        current_time = datetime.strptime(f'{start_hour}:00', '%H:%M')
        end_time = datetime.strptime(f'{end_hour}:00', '%H:%M')

        while current_time <= end_time:
            working_hours.append(current_time.strftime('%H:%M'))
            current_time += timedelta(hours=step_hours)
        return working_hours
    
    
    @classmethod
    async def get_available_slots(cls, session: AsyncSession, master_id: int, start_date: date):
        try:
            end_date = start_date + timedelta(days=6)
            working_hours = cls.generate_working_hours()

            query = select(cls.model).where(
                and_(
                    cls.model.master_id==master_id,
                    cls.model.day_booking >= start_date,
                    cls.model.day_booking <= end_date
                )
            )
            result = await session.execute(query)
            data_date = result.scalars().all()
            date_time_date = {(
                    models.day_booking.isoformat(),
                    models.time_booking.strftime('%H:%M')
                ) for models in data_date}
            
            available_slots = []
            while start_date <= end_date:
                date_iso = start_date.isoformat()

                day_slots = []
                if date_iso >= datetime.now().date().isoformat():
                    for time_str in working_hours:
                        is_available = (date_iso, time_str) not in date_time_date

                        if date_iso == datetime.now().date().isoformat():
                            slot_time = datetime.strptime(time_str, '%H:%M').time()

                            if slot_time <= datetime.now().time():
                                is_available = False
                    
                        if is_available:
                            day_slots.append(time_str)

                available_slots.append({
                    'date': date_iso,
                    'time': day_slots,
                    'total_slots': len(day_slots)
                })

                start_date += timedelta(days=1)
            return available_slots


        except BaseException as err:
            logger.error(f'Произошла ошибка: {err}')
            raise HTTPException(
                status_code=500, detail='Error while getting available slots')
    
    @classmethod
    async def book_appointment(cls, session: AsyncSession,
                               master_id: int, user_id: int, date_book: date, time_book: time):
        if user_id == master_id:
            raise HTTPException(status_code=400, detail='Нельзя записаться к себе')
        if date_book < date.today():
            raise HTTPException(status_code=400, detail='Нельзя записатьзя задним числом.')