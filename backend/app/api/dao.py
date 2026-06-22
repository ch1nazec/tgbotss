from datetime import date, timedelta, datetime, time
from fastapi import HTTPException
from loguru import logger

from pydantic import BaseModel

from sqlalchemy import select, and_, func
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import UserModel, UserCreate, MasterCreate, MasterModel
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
    
    @classmethod
    async def get_booking_user(cls, session: AsyncSession, user_id: int):
        try:

            user = UserDAO.find_one_or_none_id(user_id, session)
            if not user:
                logger.warning(f'Пользователь с ID {user_id} не найден')
                return
            
            query = select(Recording).where(
                Recording.user_id==user_id)
            result = await session.execute(query)
            result_scalars = result.scalars().all()

            return result_scalars
        except Exception as err:
            await session.rollback()
            logger.error(f'Произошла ошибка в получение записей юзера по ID {user_id}: {err}')
            raise err


class MasterDAO(BaseDAO[Master]):
    model = Master

    @classmethod
    async def user_to_master(cls, session: AsyncSession, user_id: int) -> MasterModel:
        try:
            logger.info(f'Begin to make root master of user with ID: {user_id}')
            user = await UserDAO.find_one_or_none_id(user_id, session)

            if not user:
                raise HTTPException(status_code=404, detail=f'User with id: {user_id} not found')

            master_pydantic = MasterCreate(user_id=user_id, stage=0)
            master = await cls.add(session=session, values=master_pydantic)

            await session.flush(); return master
        except Exception as err:
            if session.is_active:
                await session.rollback()

            logger.error(f'Error: {err}')
            raise err


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
            await session.flush()

            return book
        except BaseException as err:
            logger.error(f'Хуебесы отказались вас принимать. Причина: {err}')
            await session.rollback()

            raise HTTPException(
                status_code=503, detail='Сервер встал на сторону хуебесов и не хочет вас обслуживать')


class FeedbackDAO(BaseDAO[Feedback]):
    model = Feedback


    @classmethod
    async def add_more_photos(cls, session: AsyncSession,
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
    
    @classmethod
    async def get_feedbacks_by_record_id(cls, session: AsyncSession, record_id: int):
        try:
            logger.info('Поиск отзывов по записи')

            record = await RecordingDAO.find_one_or_none_id(record_id, session)
            if not record:
                logger.warning(f'Запись с ID {record_id} не найдена')
                return 

            query = select(cls.model).where(
                cls.model.record_id==record.id)
            
            result = await session.execute(query)
            result_scalars = result.scalars().all()

            return result_scalars
        except Exception as err:
            await session.rollback()
            logger.error(f'Произошла ошибка при поиске отзывов по записи: {err}')

            raise err