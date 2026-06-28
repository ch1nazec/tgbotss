from services.book_endpoint import book_router
from services.feedback_endpoint import feedback_router
from services.master_endpoint import master_router
from services.user_endpoint import user_router


all_routers = [
    book_router, feedback_router,
    master_router, user_router
]