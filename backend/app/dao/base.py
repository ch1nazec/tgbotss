from pydantic import BaseModel
from typing import TypeVar, Generic
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from app.dao.database import Base

from api.dao import UserModel


T = TypeVar('T', bound=Base)


class BaseDAO(Generic[T]):
    model: type[T]

    @classmethod
    async def find_one_or_none_id(cls, id: int, session: AsyncSession) -> UserModel:
        logger.info(f'Поиск {cls.model.__name__} класса по id: {id}')

        try:
            query = select(cls.model).filter_by(id=id)
            result = await session.execute(query)
            record = result.scalar_one_or_none()

            if record:
                logger.info(f'Запись с id {id} найдена')
            else:
                logger.info(f'Запись с id {id} не найдена')
            return record
        except SQLAlchemyError as e:
            logger.error(f'Ошибка при поиске записи {cls.model.__name__} по ID {id}: {e}')
            raise e
    

    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, filter_data: BaseModel):
        filter_dict = filter_data.model_dump(exclude_unset=True)
        logger.info(f'Поиск {cls.model.__name__} по фильтрам {filter_data}')

        try:
            query = select(cls.model).filter_by(**filter_dict)
            result = await session.execute(query)
            record = result.scalar_one_or_none()

            if record:
                logger.info(f'Запись по фильтрам найдена')
            else:
                logger.info(f'Запись по фильтрам не найдена')
            return record
        except SQLAlchemyError as e:
            logger.error(f'Ошибка при поиске по записи {cls.model.__name__} по фильтрам: {e}')
            raise e
    

    @classmethod
    async def add(cls, session: AsyncSession, values: BaseModel):
        values_dict = values.model_dump(exclude_unset=True)
        logger.info(f'Добавление записи {cls.model.__name__} с данными {values_dict}')

        new_instance = cls.model(**values_dict)
        session.add(new_instance)

        try:
            await session.flush()
            logger.info('Всё прошло успешно')
            return new_instance
        except Exception as err:
            logger.error(f'Произошла ошибка: {err}')
            await session.rollback()

            raise err
        
    
    @classmethod
    async def update_for_id(cls, session: AsyncSession, new_value: BaseModel, record_id: int):
        values_new = new_value.model_dump(exclude_unset=True)

        logger.info(f'Обновление данных объекта {cls.model}')
        try:
            recording = await cls.find_one_or_none_id(record_id, session=session)
            if not recording:
                logger.warning(f'Объект {cls.model.__name__} с ID {record_id} не найден для обновления')
                return

            for key, value in values_new.items():
                setattr(recording, key, value)

            await session.flush()
            return recording
        except Exception as err:
            logger.error(f'Произошла ошибка в модели {cls.model}: {err}')
            await session.rollback()
            raise err