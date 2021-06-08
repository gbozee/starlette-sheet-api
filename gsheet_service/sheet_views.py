import os

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from gsheet_service import (
    service,
    sheet_service,
)

BASE_DIR = os.path.dirname(os.path.abspath(__name__))

service_api = sheet_service.service_api


async def fetch_groups(request: Request):
    data = await request.json()
    result = await sheet_service.fetch_groups(**data)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


async def read_row(request: Request):
    data = await request.json()
    result: service.Result = await sheet_service.read_row(**data)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


async def read_sheetnames(request: Request):
    data = await request.json()
    result: service.Result = await sheet_service.read_sheetnames(**data)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


# async def secrets(request: Request):
#     return JSONResponse(service.config)


async def update_existing(request: Request):
    data = await request.json()
    result: service.Result = await sheet_service.update_existing(**data)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


async def read_last(request: Request):
    data = await request.json()
    result: service.Result = await sheet_service.read_last(**data)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


async def add_new(request: Request):
    data = await request.json()
    result: service.Result = await sheet_service.add_new(**data)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


async def read_new_row(request: Request):
    data = await request.json()
    result: service.Result = await sheet_service.read_new_row(**data)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


async def read_referenced_cell(request: Request):
    data = await request.json()
    result: service.Result = await sheet_service.read_referenced_cell(**data)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


async def read_new_row(request: Request):
    data = await request.json()
    result: service.Result = await sheet_service.read_new_row(**data)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


routes = [
    Route("/read-single", read_row, methods=["POST"]),
    Route("/read-new-single", read_new_row, methods=["POST"]),
    Route("/read-referenced-cells", read_referenced_cell, methods=["POST"]),
    Route("/read-sheetnames", read_sheetnames, methods=["POST"]),
    Route("/update", update_existing, methods=["POST"]),
    Route("/add", add_new, methods=["POST"]),
    Route("/read-last", read_last, methods=["POST"]),
    Route("/fetch-groups", fetch_groups, methods=["POST"]),
    # Route("/secrets", secrets),
]


async def on_startup_task():
    if service_api:
        await service_api.db_action("connect")


async def on_shutdown_task():
    if service_api:
        await service_api.db_action("disconnect")


on_startup = [on_startup_task]
on_shutdown = [on_shutdown_task]