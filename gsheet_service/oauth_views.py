import typing
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse
from gsheet_service import oauth_service


async def authorization_view(request: Request):
    provider = request.path_params["provider"]
    body = await request.json()
    result: oauth_service.Result = await oauth_service.get_authorization_url(
        provider, **body
    )
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


async def access_token_view(request: Request):
    provider = request.path_params["provider"]
    body = await request.json()
    result: oauth_service.Result = await oauth_service.get_access_and_refresh_token(
        provider, **body
    )
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


async def refresh_token(request: Request):
    provider = request.path_params["provider"]
    body = await request.json()
    result: oauth_service.Result = await oauth_service.refresh_token(provider, **body)
    if result.error:
        return JSONResponse({"status": False, "msg": result.error}, status_code=400)
    return JSONResponse({"status": True, "data": result.data})


routes = [
    Route("/{provider}/authorize", authorization_view, methods=["POST"]),
    Route("/{provider}/get-token", access_token_view, methods=["POST"]),
    Route("/{provider}/refresh-token", refresh_token, methods=["POST"]),
]
