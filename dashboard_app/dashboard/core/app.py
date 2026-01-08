from fastapi import FastAPI
from dashboard_app.dashboard.routes.pages import pages_router
from dashboard_app.dashboard.routes.profile import profile_router
from dashboard_app.dashboard.routes.widgets import widgets_router

dashboard_app = FastAPI()

dashboard_app.include_router(pages_router)
dashboard_app.include_router(profile_router)
dashboard_app.include_router(widgets_router)