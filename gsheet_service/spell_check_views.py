from starlette.requests import Request
from starlette.routing import Route
from starlette.responses import JSONResponse
from gsheet_service import spell_check_service as service


async def spell_check(request: Request):
    data = await request.json()
    result: service.Result = await service.process_spell_check(**data)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


routes = [Route("/evaluate", spell_check, methods=["POST"])]

on_startup = []
on_shutdown_task = []