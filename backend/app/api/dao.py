from datetime import date, timedelta, datetime, time
from fastapi import HTTPException
from loguru import logger

from pydantic import BaseModel

from sqlalchemy import select, and_, func
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import UserModel, UserCreate
from app.dao.base import BaseDAO
from app.dao.models import User, Recording, Master, Feedback, PhotoFeedback


class PhotoFeedbackDAO(BaseDAO[PhotoFeedback]):
    model = PhotoFeedback


class UserDAO(BaseDAO[User]):
    model = User

    @classmethod
    async def create_or_get(cls, session: AsyncSession, user_data: UserCreate) -> UserModel:
        try:
            result = await cls.find_one_or_none(session=session, filter_data=user_data)
            if not result:
                raise NoResultFound
            else:
                return result
        except NoResultFound:
            user_model = cls.model(**user_data.model_dump(exclude_unset=True))
            await cls.add(session, user_model)
            return user_model
        
        except Exception as err:
            logger.error(f'Ошибка: {err}')
            raise err


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
    async def check_book(cls, session: AsyncSession, user_id: int, date_book: date, time_book: time):
        try:
            query = select(cls.model).where(
                cls.model.user_id == user_id,
                cls.model.day_booking == date_book,
                cls.model.time_booking == time_book
            )
            result = await session.execute(query)
            result_scalar = result.scalars().all()

            return True if result_scalar else False
        except BaseException as err:
            logger.error(f'Хуебесы отказываются искать записи пользователя к мастурбаторам: {err}')
            raise HTTPException(
                status_code=503, detail='Сервер встал на сторону хуебесов и не хочет вас обслуживать')
    
    @classmethod
    async def book_appointment(cls, session: AsyncSession,
                               master_id: int, user_id: int, date_book: date, time_book: time):
        if user_id == master_id:
            raise HTTPException(status_code=400, detail='Нельзя записаться к себе')
        if date_book < date.today():
            raise HTTPException(status_code=400, detail='Нельзя записатьзя задним числом. Хуебесы будут злиться!')
        
        try:
            query = select(cls.model).where(
                cls.model.master_id == master_id,
                cls.model.time_booking == time_book,
                cls.model.day_booking == date_book
                )
            result = await session.execute(query)
            existing_booking = result.scalar_one_or_none()

            if existing_booking:
                raise HTTPException(status_code=400, detail='Запись такая уже есть.')
            user_books = await cls.check_book(session=session, user_id=user_id, time_book=time_book, date_book=date_book)
            if user_books:
                raise HTTPException(status_code=400, detail='Вы записаны к другому мастеру.')

            book = cls.model(
                master_id=master_id, user_id=user_id, day_booking=date_book, time_booking=time_book)
            session.add(book)
            await session.commit()

            return book
        except BaseException as err:
            logger.error(f'Хуебесы отказались вас принимать. Причина: {err}')
            await session.rollback()

            raise HTTPException(
                status_code=503, detail='Сервер встал на сторону хуебесов и не хочет вас обслуживать')


class FeedbackDAO(BaseDAO[Feedback]):
    model = Feedback


    @classmethod
    async def add_moro_photos(cls, session: AsyncSession,
                              feedback_data: BaseModel,
                              path_url: list[str]):
        try:
            feedback_dict = feedback_data.model_dump(exclude_unset=True)

            new_feedback = cls.model(**feedback_dict)

            new_feedback.photofeedback = [
                path for path in path_url]
            session.add(new_feedback)

            await session.flush()
            logger.info('Всё успешно загружено.')
        except BaseException as err:
            await session.rollback()

            logger.error(f'Произошла ошибка {cls.model.__name__} с данными: {err}')
            raise err