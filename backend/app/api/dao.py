from datetime import date, timedelta, datetime, time, timezone
from typing import List
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
    async def get_available_slots(cls, session: AsyncSession, user_id: int, master_id: int, start_date: date):
        try:
            if user_id == master_id:
                raise HTTPException(status_code=304, detail='Вы не можете записаться на себя')
            
            start_week = start_date - timedelta(days=start_date.weekday())
            end_of_week = start_date + timedelta(days=5)

            query = select(cls.model).where(
                and_(
                    cls.model.master_id == master_id,
                    cls.model.day_booking >= start_date,
                    cls.model.day_booking <= end_of_week
                )
            )
            result = await session.execute(query)
            existings_books = result.scalars().all()

            working_hours = cls.generate_working_hours()
            booked_busy = {
                (
                    book.day_booking.strftime('%d-%m'),
                    book.time_booking.strftime('%H:%M')
                )
                for book in existings_books
            }

            week_days_rus = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
            availables_slots = []

            for i in range(len(week_days_rus)):
                ...
        except:
            ...