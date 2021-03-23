import typing
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse
from gsheet_service import media_service, settings

async def upload_image(request: Request):
    identifier = request.path_params["identifier"]
    content_type = request.headers['content-type']
    if content_type == 'application/json':
        data = await request.json()
    else:
        form_data = await request.form()
        contents = await form_data["image"].read()
        data = {"image": contents}
    result = await media_service.create_cloudinary_image(identifier, **data)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})

async def upload_video(request: Request):
    identifier = request.path_params["identifier"]
    content_type = request.headers['content-type']
    if content_type != 'application/json':
        form_data = await request.form()
        contents = await form_data["video"].read()
        data = {"video": contents}
    result = await media_service.create_cloudinary_video(identifier, **data)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})

async def upload_audio(request: Request):
    identifier = request.path_params["identifier"]
    content_type = request.headers['content-type']
    if content_type != 'application/json':
        form_data = await request.form()
        contents = await form_data["audio"].read()
        data = {"audio": contents}
    result = await media_service.create_cloudinary_audio(identifier, **data)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})

async def get_image_url(request: Request):
    identifier = request.path_params["identifier"]
    data = await request.json()
    public_id = data.pop("public_id", None)
    result = await media_service.get_cloudinary_url(identifier, public_id, **data)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})

async def get_audio_url(request: Request):
    identifier = request.path_params["identifier"]
    data = await request.json()
    public_id = data.pop("public_id", None)
    result = await media_service.get_audio_url(identifier, public_id, **data)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})

async def get_video_url(request: Request):
    identifier = request.path_params["identifier"]
    data = await request.json()
    public_id = data.pop("public_id", None)
    result = await media_service.get_video_url(identifier, public_id, **data)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


async def delete_resource(request: Request):
    identifier = request.path_params["identifier"]
    data = await request.json()
    public_id = data.pop("public_id", None)
    result = await media_service.delete_cloudinary_resource(
        identifier, public_id, **data
    )
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


routes = [
    Route("/{identifier}/upload", upload_image, methods=["POST"]),
    Route("/{identifier}/upload_video", upload_video, methods=["POST"]),
    Route("/{identifier}/upload_audio", upload_audio, methods=["POST"]),
    Route("/{identifier}/get_url", get_image_url, methods=["POST"]),
    Route("/{identifier}/get_audio_url", get_audio_url, methods=["POST"]),
    Route("/{identifier}/get_video_url", get_video_url, methods=["POST"]),
    Route("/{identifier}/delete", delete_resource, methods=["POST"]),
]

