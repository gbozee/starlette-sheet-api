import os

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from gsheet_service import (
    media_views,
    oauth_views,
    scheduler_views,
    settings,
    sheet_views,
)

BASE_DIR = os.path.dirname(os.path.abspath(__name__))

templates = Jinja2Templates(
    directory=os.path.join(BASE_DIR, "gsheet_service", "templates")
)


def oauth_config():
    link = settings.OAUTH_SPREADSHEET
    sheet = settings.OAUTH_SHEET_NAME
    redirect_uri = f"{settings.HOST_PROVIDER}/redirect"
    return locals()


async def home(request: Request):
    result = await oauth_views.oauth_service.get_authorization_url(
        "zoho", **oauth_config()
    )
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "authorization_url": result.data["authorization_url"],
        },
    )


async def fetch_access_token(request: Request):
    body = await request.json()
    authorization_response = body.get("redirect_uri")
    if not authorization_response:
        return JSONResponse(
            {"status": False, "msg": "No redirect_uri passed"}, status_code=400
        )
    result = await oauth_views.oauth_service.get_access_and_refresh_token(
        "zoho",
        authorization_response=authorization_response,
        **oauth_config(),
    )
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


async def get_emails(request: Request):
    body = await request.json()
    refresh_token = body.get("refresh_token")
    search_config = body.get("search_config")
    provider = request.path_params["provider"]
    if not refresh_token:
        return JSONResponse(
            {"status": False, "msg": "No refresh_token sent"}, status_code=400
        )
    if not search_config:
        return JSONResponse(
            {"status": False, "msg": "No search_config sent"}, status_code=400
        )
    result = await oauth_views.oauth_service.get_emails(
        provider,
        search_config=search_config,
        refresh_token=refresh_token,
        **oauth_config(),
    )
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


async def get_email_content(request: Request):
    body = await request.json()
    refresh_token = body.get("refresh_token")
    email_data = body.get("email_data")
    provider = request.path_params["provider"]
    if not refresh_token:
        return JSONResponse(
            {"status": False, "msg": "No refresh_token sent"}, status_code=400
        )
    if not email_data:
        return JSONResponse(
            {"status": False, "msg": "No email_data content sent"}, status_code=400
        )
    result = await oauth_views.oauth_service.get_email_content(
        provider, email_data, refresh_token=refresh_token, **oauth_config()
    )
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


def redirect_page(request: Request):
    return templates.TemplateResponse("redirect.html", {"request": request})


# async def secrets(request: Request):
#     return JSONResponse(service.config)


async def oauth_callback(request: Request):
    params = dict(request.query_params)
    return JSONResponse(params)


middlewares = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_headers=["*"],
        allow_methods=["*"],
        allow_credentials=True,
    )
]

routes = [
    Route("/", home),
    Route("/redirect", redirect_page),
    Route("/get-access-token", fetch_access_token, methods=["POST"]),
    Route("/{provider}/get-emails", get_emails, methods=["POST"]),
    Route("/{provider}/get-email-content", get_email_content, methods=["POST"]),
    Mount(
        "/static",
        StaticFiles(directory=os.path.join(BASE_DIR, "gsheet_service", "static")),
        name="static",
    ),
    Route("/oauth-callback", oauth_callback, methods=["GET"]),
    Mount("/oauth", routes=oauth_views.routes),
    Mount("/media", routes=media_views.routes),
    Mount("/scheduler", routes=scheduler_views.routes),
    Mount("", routes=sheet_views.routes),
    # Route("/secrets", secrets),
]


on_startup = [] + sheet_views.on_startup
on_shutdown = [] + sheet_views.on_shutdown

app = Starlette(
    middleware=middlewares,
    routes=routes,
    on_startup=on_startup,
    on_shutdown=on_shutdown,
)
