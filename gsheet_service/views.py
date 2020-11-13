import typing

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.routing import Route, Mount
from gsheet_service import service, oauth_views, settings
import os
import json

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
        {"request": request, "authorization_url": result.data["authorization_url"],},
    )


async def fetch_access_token(request: Request):
    body = await request.json()
    authorization_response = body.get("redirect_uri")
    if not authorization_response:
        return JSONResponse(
            {"status": False, "msg": "No redirect_uri passed"}, status_code=400
        )
    result = await oauth_views.oauth_service.get_access_and_refresh_token(
        "zoho", authorization_response=authorization_response, **oauth_config(),
    )
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


async def get_emails(request: Request):
    body = await request.json()
    refresh_token = body.get("refresh_token")
    search_config = body.get("search_config")
    provider = request.path_params['provider']
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
    provider = request.path_params['provider']
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


async def fetch_groups(request: Request):
    data = await request.json()
    link = data.get("link")
    sheet = data.get("sheet")
    segments = data.get("segments") or []
    result: service.Result = await service.fetch_groups(link, sheet, segments)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


async def read_row(request: Request):
    data = await request.json()
    link = data.get("link")
    primary_key = data.get("key")
    value = data.get("value")
    sheet = data.get("sheet")
    result: service.Result = await service.read_row(link, sheet, primary_key, value)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


async def read_sheetnames(request: Request):
    data = await request.json()
    link = data.get("link")
    result: service.Result = await service.read_sheetnames(link)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


# async def secrets(request: Request):
#     return JSONResponse(service.config)


async def update_existing(request: Request):
    data = await request.json()
    link = data.get("link")
    sheet = data.get("sheet")
    key = data.get("key")
    value = data.get("value")
    update_data = data.get("data")
    result: service.Result = await service.update_row(
        link, sheet, key, value, update_data
    )
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


async def read_last(request: Request):
    data = await request.json()
    link = data.get("link")
    sheet = data.get("sheet")
    result: service.Result = await service.read_last_row(link, sheet)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


async def add_new(request: Request):
    data = await request.json()
    link = data.get("link")
    sheet = data.get("sheet")
    update_data = data.get("data")
    result: service.Result = await service.add_to_sheet(link, sheet, update_data)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})

async def read_new_row(request: Request):
    data = await request.json()
    link = data.get("link")
    primary_key = data.get("key")
    value = data.get("value")
    sheet = data.get("sheet")
    page_size = data.get("page_size") or 20
    page = data.get("page") or 1
    result: service.Result = await service.read_new_row(link, sheet, page_size=page_size, page=page,  key=primary_key, value=value)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})

async def read_referenced_cell(request: Request):
    data = await request.json()
    link = data.get("link")
    primary_key = data.get("key")
    value = data.get("value")
    sheet = data.get("sheet")
    options = data.get("options")
    result: service.Result = await service.read_referenced_cell(link, sheet, key=primary_key, options=options, value=value)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})



async def read_new_row(request: Request):
    data = await request.json()
    link = data.get("link")
    primary_key = data.get("key")
    value = data.get("value")
    sheet = data.get("sheet")
    page_size = data.get("page_size") or 20
    page = data.get("page") or 1
    result: service.Result = await service.read_new_row(
        link, sheet, page_size=page_size, page=page, key=primary_key, value=value
    )
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


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
    Route("/read-single", read_row, methods=["POST"]),
    Route("/read-new-single", read_new_row, methods=["POST"]),
    Route("/read-referenced-cells", read_referenced_cell, methods=["POST"]),
    Route("/read-sheetnames", read_sheetnames, methods=["POST"]),
    Route("/update", update_existing, methods=["POST"]),
    Route("/add", add_new, methods=["POST"]),
    Route("/read-last", read_last, methods=["POST"]),
    Route("/fetch-groups", fetch_groups, methods=["POST"]),
    Mount("/oauth", routes=oauth_views.routes)
    # Route("/secrets", secrets),
]

app = Starlette(middleware=middlewares, routes=routes)
