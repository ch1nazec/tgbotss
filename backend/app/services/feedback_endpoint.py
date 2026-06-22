import uuid, os, aiofiles
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from api.schemas import FeedbackCreate, FeedbackModel, PhotoFeedbackModel, PhotoFeedbackCreate

from api.dao import FeedbackDAO, RecordingDAO, PhotoFeedbackDAO
from dao.sessionmake_fastapi import DatabaseSession
from sqlalchemy.ext.asyncio import AsyncSession

from utils.helpers import response_wrapper_result, ALLOWED_EXTENSIONS, UPLOAD_DIR


feedback_router = APIRouter(prefix='/feedback')


@feedback_router.get('/{record_id}', response_model=list[FeedbackModel])
async def feedbacks_record(
    record_id: int,
    session: AsyncSession = Depends(DatabaseSession.get_db)
    ):
    feedbacks = await FeedbackDAO.get_feedbacks_by_record_id(
        session=session, record_id=record_id)
    return feedbacks


@feedback_router.post('/add', response_model=FeedbackModel)
async def feedback_add(
    feedback: FeedbackCreate,
    session: AsyncSession = Depends(DatabaseSession.get_db_with_commit)
    ):
    feedback_post = await FeedbackDAO.add(session=session, values=feedback.model_dump())
    return feedback_post


@feedback_router.post('/{feedback_id}/upload-photo/')
async def upload_photo_feedbacks(
    feedback_id: int,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(DatabaseSession.get_db_with_commit)):

    try:
        feedback = await FeedbackDAO.find_one_or_none_id(id=feedback_id, session=session)
        if not feedback:
            raise HTTPException(status_code=404, detail='Отзыв не найден.')
        
        if file.content_type not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail='Неподдерживаемый формат фото.')
        
        file_extensions = file.filename.split('.')[-1]
        file_name = f'{uuid.uuid4()}.{file_extensions}'
        file_path = os.path.join(UPLOAD_DIR, file_name)

        async with aiofiles.open(file_path, 'wb') as buffer:
            content = await file.read()
            await buffer.write(content)
        
        photo_feedback_pydantic = PhotoFeedbackCreate(photo=file_name, feedback_id=feedback_id)
        feedback_photo = await PhotoFeedbackDAO.add(photo_feedback_pydantic, session=session)
        
        return JSONResponse(
            status_code=201,
            content={"message": "Фото успешно выложено.", "photo": file_name}
        )
    except Exception as err:
        if os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(
            status_code=500, 
            detail=f'Ошибка сохранения данных в БД. Файл удален. Текст ошибки: {str(err)}'
        )