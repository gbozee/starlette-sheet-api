import typing
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse
from gsheet_service import scheduler_service, settings


async def create_job(request: Request):
    identifier = request.path_params["identifier"]
    data = await request.json()
    result = await scheduler_service.create_job(identifier, **data)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


async def pause_job(request: Request):
    identifier = request.path_params["identifier"]
    data = await request.json()
    result = await scheduler_service.pause_job(identifier, **data)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


async def resume_job(request: Request):
    identifier = request.path_params["identifier"]
    data = await request.json()
    result = await scheduler_service.resume_job(identifier, **data)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


async def delete_job(request: Request):
    identifier = request.path_params["identifier"]
    data = await request.json()
    result = await scheduler_service.delete_job(identifier, **data)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


async def list_jobs(request: Request):
    identifier = request.path_params["identifier"]
    data = await request.json()
    result = await scheduler_service.get_all_jobs(identifier, **data)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    import pdb; pdb.set_trace()
    return JSONResponse({"status": True, "data": result.data})


async def single_job(request: Request):
    identifier = request.path_params["identifier"]
    job_id = request.path_params["job_id"]
    data = await request.json()
    result = await scheduler_service.get_job(identifier, job_id, **data)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


routes = [
    Route("/{identifier}/jobs/create", create_job, methods=["POST"]),
    Route("/{identifier}/jobs/pause", pause_job, methods=["POST"]),
    Route("/{identifier}/jobs/resume", resume_job, methods=["POST"]),
    Route("/{identifier}/jobs/delete", delete_job, methods=["POST"]),
    Route("/{identifier}/jobs", list_jobs, methods=["POST"]),
    Route("/{identifier}/jobs/{job_id}", single_job, methods=["POST"]),
]