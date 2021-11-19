import typing
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse
from gsheet_service import media_service, settings

# working well


async def upload_resource(request: Request):
    identifier = request.path_params["identifier"]
    content_type = request.headers["content-type"]
    if content_type == "application/json":
        data = await request.json()
        kind = data.pop("kind", None)
        if kind == "audio":
            result = await media_service.create_cloudinary_audio(identifier, **data)
        elif kind == "video":
            result = await media_service.create_cloudinary_video(identifier, **data)
        else:
            result = await media_service.create_cloudinary_image(identifier, **data)
    else:
        form_data = await request.form()
        params = list(form_data.keys())
        if params:
            kind = params[0]
            data = dict(form_data)
            kind = data.pop("kind", None) or kind
            if kind == "audio":
                data["audio"] = await form_data["audio"].read()
                result = await media_service.create_cloudinary_audio(identifier, **data)
            elif kind == "video":
                data["video"] = await form_data["video"].read()
                result = await media_service.create_cloudinary_video(identifier, **data)
            else:
                data["image"] = await form_data["image"].read()
                result = await media_service.create_cloudinary_image(identifier, **data)
            if result.error:
                return JSONResponse(
                    {"status": False, "msg": result.error}, status_code=400
                )
            return JSONResponse({"status": True, "data": result.data})
        if not params:
            return JSONResponse(
                {"status": False, "msg_data": {"params": params}}, status_code=400
            )
        return JSONResponse(
            {"status": False, "msg": "Error from server"}, status_code=400
        )


async def get_cloudinary_url(request: Request):
    identifier = request.path_params["identifier"]
    data = await request.json()
    kind = data.pop("kind", "image")
    public_id = data.pop("public_id", None)
    result = await media_service.get_cloudinary_url(identifier, kind, public_id, **data)
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
    Route("/{identifier}/upload", upload_resource, methods=["POST"]),
    Route("/{identifier}/get_url", get_cloudinary_url, methods=["POST"]),
    Route("/{identifier}/delete", delete_resource, methods=["POST"]),
]
