from datetime import date
from typing import List
from sqlalchemy import Integer, Text, ForeignKey, String, Date, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.dao.database import Base


class User(Base):
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True)

    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    third_name: Mapped[str] = mapped_column(String(100), nullable=True)
    
    date_birth: Mapped[date] = mapped_column(Date, nullable=False)

    master: Mapped['Master'] = relationship(back_populates='user', uselist=False, cascade='all, delete-orphan')
    records: Mapped[List['Recording']] = relationship(back_populates='user', cascade='all, delete-orphan')

    __table_args__ = (
        Index('ix_user_telegram_id', 'telegram_id'),)



class Master(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), unique=True)
    user: Mapped['User'] = relationship(back_populates='master')
    stage: Mapped[int]

    records: Mapped[List['Recording']] = relationship(back_populates='master')

    __table_args__ = (
        Index('ix_master_user_id', 'user_id'),)


class Recording(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'))
    user: Mapped['User'] = relationship(back_populates='records')

    master_id: Mapped[int] = mapped_column(ForeignKey('masters.id', ondelete='CASCADE'))
    master: Mapped['Master'] = relationship(back_populates='records')

    feedback: Mapped['Feedback'] = relationship(back_populates='record')

    __table_args__ = (
        Index('ix_recording_user_id', 'user_id'),
        Index('ix_recording_master_id', 'master_id'),)


class Feedback(Base):
    rating: Mapped[int] = mapped_column(
        Integer, CheckConstraint('rating BETWEEN 1 AND 5'),
        nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True, )

    record: Mapped['Recording'] = relationship(back_populates='feedback')
    record_id: Mapped[int] = mapped_column(ForeignKey('recordings.id'))

    photofeedback: Mapped[List['PhotoFeedback']] = relationship(back_populates='feedbacks')


class PhotoFeedback(Base):
    photo: Mapped[str] = mapped_column(String(500), nullable=False)

    feedback: Mapped['Feedback'] = relationship(back_populates='photofeedback', uselist=False)
    feedback_id: Mapped[int] = mapped_column(ForeignKey('feedbacks.id', ondelete='CASCADE'))

    __table_args__ = (
        Index('ix_photofeedback_feedback_id', 'feedback_id'))