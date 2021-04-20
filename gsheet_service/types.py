import typing
import json
from gsheet_service import settings, models


class Result:
    def __init__(
        self,
        error: str = None,
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


async def get_provider_sheet(link=None, sheet=None, provider=None, key="id", **kwargs):
    updated_config = {**config, **kwargs}
    instance = models.GoogleSheetInterface(**updated_config)
    instance.load_file(link, sheet)
    result = instance.get_all_records()
    if key:
        found = [x for x in result if x[key].lower() == provider.lower()]
        if found:
            return found[0]
    return None
