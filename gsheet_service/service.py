import typing
import json

from gsheet_service import settings, models


class Result:
    def __init__(
        self,
        error: dict = None,
        data: dict = None,
        task: typing.List[typing.Any] = None,
    ):
        self.error = error
        self.data = data
        self.task = task


config = dict(
    project_id=settings.GOOGLE_PROJECT_ID,
    private_key=settings.GOOGLE_PRIVATE_KEY,
    private_key_id=settings.GOOGLE_PRIVATE_KEY_ID,
    client_email=settings.GOOGLE_CLIENT_EMAIL,
    client_id=settings.GOOGLE_CLIENT_ID,
)

if not settings.DEBUG:
    config.update(private_key=json.loads(f'{config["private_key"]}'))
else:
    config.update(private_key=json.loads(f'"{config["private_key"]}"'))


async def read_row(link, sheet, key, value) -> Result:
    if not link or not sheet:
        return Result(error="Missing `link` or `sheet` value")
    instance = models.GoogleSheetInterface(**config)
    instance.load_file(link, sheet)
    result = instance.get_all_records()
    if value:
        if not key:
            return Result(error="Missing `key` field to read a single record")
        found = [x for x in result if x[key] == value]
        if found:
            return Result(data=found[0])
    return Result(data=result)


async def update_row(link, sheet, key, value, data) -> Result:
    if not link or not sheet:
        return Result(error="Missing `link` or `sheet` value")
    instance = models.GoogleSheetInterface(**config)
    instance.load_file(link, sheet)
    if value:
        if not key:
            return Result(error="Missing `key` field to read a record")
        try:
            instance.update_existing_record(key, value, data)
        except KeyError as e:
            return Result(error="Wrong `key` passed in `data`")
        else:
            return await read_row(link, sheet, key, value)
