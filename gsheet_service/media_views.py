import typing
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse
from gsheet_service import media_service, settings


async def upload_image(request: Request):
    identifier = request.path_params["identifier"]
    data = await request.json()
    result = await media_service.create_cloudinary_image(identifier, **data)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


async def get_image_url(request: Request):
    identifier = request.path_params["identifier"]
    public_id = request.path_params["public_id"]
    data = dict(request.query_params)
    result = await media_service.get_cloudinary_url(identifer, public_id, **data)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


async def delete_image(request: Request):
    identifier = request.path_params["identifier"]
    public_id = request.path_params["public_id"]
    data = await request.json()
    result = await media_service.delete_cloudinary_resource(
        identifier, public_id, **data
    )
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


routes = [
    Route("/{identifier}/upload", upload_image, methods=["POST"]),
    Route("/{identifier}/get_url/{public_id}", get_image_url, methods=["GET"]),
    Route("/{identifier}/delete/{public_id}", delete_image, methods=["POST"]),
]

