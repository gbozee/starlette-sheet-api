from gsheet_service import service, settings
import jwt


def encode_obj(obj):
    return jwt.encode(obj, settings.SECRET, algorithm="HS256")


async def fetch_group(**data) -> service.Result:
    link = data.get("link")
    sheet = data.get("sheet")
    segments = data.get("segments") or []
    result: service.Result = await service.fetch_groups(link, sheet, segments)
