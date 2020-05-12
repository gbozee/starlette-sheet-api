import typing

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from gsheet_service import service


def home(request: Request):
    return JSONResponse({"hello": "world"})


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
    Route("/read-single", read_row, methods=["POST"]),
    Route("/update", update_existing, methods=["POST"])
    # Route("/secrets", secrets),
]

app = Starlette(middleware=middlewares, routes=routes)
