import jwt

from gsheet_service import app_models, service, settings

service_api = None

if settings.DATABASE_URL:
    service_api = app_models.ServiceAPI(settings.DATABASE_URL)


def encode_obj(obj):
    result = jwt.encode(obj, settings.SECRET, algorithm="HS256")
    return result.decode("utf-8")


async def check_database(request_id, callback) -> service.Result:
    if service_api:
        result = await service_api.get_record(request_id)
        if result:
            return service.Result(data=result)
    data = await callback()
    if data.data:
        if service_api:
            await service_api.update_record(request_id, data.data)
    return data


async def fetch_groups(**data) -> service.Result:
    link = data.get("link")
    sheet = data.get("sheet")
    segments = data.get("segments") or []
    key = encode_obj({**data, "method": "fetch_groups"})
    callback = lambda: service.fetch_groups(link, sheet, segments)
    return await check_database(key, callback)


async def read_row(**data):
    link = data.get("link")
    primary_key = data.get("key")
    value = data.get("value")
    sheet = data.get("sheet")
    key = encode_obj({**data, "method": "read_row"})
    callback = lambda: service.read_row(link, sheet, primary_key, value)
    return await check_database(key, callback)


async def read_sheetnames(**data):
    link = data.get("link")
    key = encode_obj({**data, "method": "read_sheetnames"})
    callback = lambda: service.read_sheetnames(link)
    return await check_database(key, callback)


async def update_existing(**data):
    link = data.get("link")
    sheet = data.get("sheet")
    key = data.get("key")
    value = data.get("value")
    update_data = data.get("data")
    key = encode_obj({**data, "method": "update_existing"})
    callback = lambda: service.update_row(link, sheet, key, value, update_data)
    return await callback()
    # return await check_database(key, callback)


async def read_last(**data):
    link = data.get("link")
    sheet = data.get("sheet")
    key = encode_obj({**data, "method": "read_last"})
    callback = lambda: service.read_last_row(link, sheet)
    return await check_database(key, callback)


async def add_new(**data):
    link = data.get("link")
    sheet = data.get("sheet")
    update_data = data.get("data")
    key = encode_obj({**data, "method": "add_new"})
    callback = lambda: service.add_to_sheet(link, sheet, update_data)
    return await check_database(key, callback)


async def read_new_row(**data):
    link = data.get("link")
    primary_key = data.get("key")
    value = data.get("value")
    sheet = data.get("sheet")
    page_size = data.get("page_size") or 20
    page = data.get("page") or 1
    key = encode_obj({**data, "method": "read_new_row"})
    callback = lambda: service.read_new_row(
        link, sheet, page_size=page_size, page=page, key=primary_key, value=value
    )
    return await check_database(key, callback)


async def read_referenced_cell(**data):
    link = data.get("link")
    primary_key = data.get("key")
    value = data.get("value")
    sheet = data.get("sheet")
    options = data.get("options")
    key = encode_obj({**data, "method": "read_referenced_cell"})
    callback = lambda: service.read_referenced_cell(
        link, sheet, key=primary_key, options=options, value=value
    )
    return await check_database(key, callback)


async def read_new_row(**data):
    link = data.get("link")
    primary_key = data.get("key")
    value = data.get("value")
    sheet = data.get("sheet")
    page_size = data.get("page_size") or 20
    page = data.get("page") or 1
    key = encode_obj({**data, "method": "read_new_row"})
    callback = lambda: service.read_new_row(
        link, sheet, page_size=page_size, page=page, key=primary_key, value=value
    )

    return await check_database(key, callback)


async def clear_database(**data):
    if service_api:
        await service_api.purge_db()
    return service.Result(data={"cleaned_db": True})
