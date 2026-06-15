from typing import List, Any, TypeVar, Generic
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from app.dao.database import Base


T = TypeVar('T', bound=Base)


class BaseDAO(Generic[T]):
    model: type[T]

    @classmethod
    async def find_one_or_none_id(cls, id: int, session: AsyncSession):
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
            raise
    

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