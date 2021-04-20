import typing
import json
from gsheet_service import settings, models, media_utils
from gsheet_service.types import Result, config, get_provider_sheet


async def get_credentials(_id, link=None, sheet=None, credentials=None, **kwargs):
    custom_credentials = {}
    if credentials:
        custom_credentials = credentials
    provider_instance = await get_provider_sheet(link, sheet, _id, **custom_credentials)
    if not provider_instance:
        return Result(error="Could not find provider in link provided")
    return provider_instance


async def create_cloudinary_image(identifier, **data) -> Result:
    server_config = data.pop("server_config", {})
    link = data.pop("link", None) or settings.MEDIA_SPREADSHEET
    sheet = data.pop("sheet", None) or settings.MEDIA_SHEET_NAME
    image = data.pop("image", None)
    resource_type = data.pop("resource_type", None) or "image"
    if server_config:
        config = server_config
    else:
        config = await get_provider_sheet(link=link, sheet=sheet, provider=identifier)
    if image and config:
        result = media_utils.MediaServiceAPI.create_resource(
            image, config=config, resource_type=resource_type, **data
        )
        return Result(data=result)
    return Result(
        error="Error creating the image in cloudinary, missing image or invalid config"
    )

async def create_cloudinary_video(identifier, **data) -> Result:
    server_config = data.pop("server_config", {})
    link = data.pop("link", None) or settings.MEDIA_SPREADSHEET
    sheet = data.pop("sheet", None) or settings.MEDIA_SHEET_NAME
    video = data.pop("video", None)
    resource_type = data.pop("resource_type", None) or "video"
    if server_config:
        config = server_config
    else:
        config = await get_provider_sheet(link=link, sheet=sheet, provider=identifier)
    if video and config:
        result = media_utils.MediaServiceAPI.create_resource(
            video, config=config, resource_type=resource_type, **data
        )
        return Result(data=result)
    return Result(
        error="Error creating the video in cloudinary, missing video or invalid config"
    )

async def create_cloudinary_video(identifier, **data) -> Result:
    server_config = data.pop("server_config", {})
    link = data.pop("link", None) or settings.MEDIA_SPREADSHEET
    sheet = data.pop("sheet", None) or settings.MEDIA_SHEET_NAME
    video = data.pop("video", None)
    resource_type = data.pop("resource_type", None) or "video"
    if server_config:
        config = server_config
    else:
        config = await get_provider_sheet(link=link, sheet=sheet, provider=identifier)
    if video and config:
        result = media_utils.MediaServiceAPI.create_resource(
            video, config=config, resource_type=resource_type, **data
        )
        return Result(data=result)
    return Result(
        error="Error creating the video in cloudinary, missing video or invalid config"
    )


async def create_cloudinary_audio(identifier, **data) -> Result:
    server_config = data.pop("server_config", {})
    link = data.pop("link", None) or settings.MEDIA_SPREADSHEET
    sheet = data.pop("sheet", None) or settings.MEDIA_SHEET_NAME
    audio = data.pop("audio", None)
    resource_type = data.pop("resource_type", None) or "raw"
    if server_config:
        config = server_config
    else:
        config = await get_provider_sheet(link=link, sheet=sheet, provider=identifier)
    if audio and config:
        result = media_utils.MediaServiceAPI.create_resource(
            audio, config=config, resource_type=resource_type, **data
        )
        return Result(data=result)
    return Result(
        error="Error creating the audio in cloudinary, missing audio or invalid config"
    )


async def get_cloudinary_url(identifier, kind, public_id, **data) -> Result:
    server_config = data.pop("server_config", {})
    link = data.pop("link", None) or settings.MEDIA_SPREADSHEET
    sheet = data.pop("sheet", None) or settings.MEDIA_SHEET_NAME
    if server_config:
        config = server_config
    else:
        config = await get_provider_sheet(link=link, sheet=sheet, provider=identifier)
    if public_id and config:
        instance = media_utils.MediaServiceAPI.get_instance(
            resource_id=public_id, kind=kind, config=config
        )
        return Result(data=instance.build_url(secure=True, **data))
    return Result(
        error="Error getting the image in cloudinary, missing public_id or invalid config"
    )

async def delete_cloudinary_resource(identifier, public_id, **data) -> Result:
    server_config = data.pop("server_config", {})
    link = data.pop("link", None) or settings.MEDIA_SPREADSHEET
    sheet = data.pop("sheet", None) or settings.MEDIA_SHEET_NAME
    kind = data.pop("kind", None) or "image"
    if server_config:
        config = server_config
    else:
        config = await get_provider_sheet(link=link, sheet=sheet, provider=identifier)
    if public_id and config:
        instance = media_utils.MediaServiceAPI.get_instance(
            resource_id=public_id, kind=kind, config=config
        )
        instance.delete()
        return Result(data={"msg": "Successful"})
    return Result(
        error="Error deleting the resource in cloudinary, missing public_id or invalid config"
    )
