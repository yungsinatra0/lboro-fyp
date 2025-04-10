from .auth import router as auth_router
from .user import router as user_router
from .file import router as file_router
from .vaccine import router as vaccine_router
from .allergy import router as allergy_router
from .healthdata import router as healthdata_router
from .medication import router as medication_router
from .dashboard import router as dashboard_router
from .medhistory import router as medhistory_router
from .labs import router as labs_router
from .share import router as share_router

def get_all_routers():
    return [
        auth_router,
        user_router,
        file_router,
        vaccine_router,
        allergy_router,
        healthdata_router,
        medication_router,
        dashboard_router,
        medhistory_router,
        labs_router,
        share_router
    ]