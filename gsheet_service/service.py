import typing
import json

from gsheet_service import settings, models
from gsheet_service.types import Result, config


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
        return Result(error="Missing result")
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


async def read_last_row(link, sheet) -> Result:
    if not link or not sheet:
        return Result(error="Missing `link` or `sheet` value")
    instance = models.GoogleSheetInterface(**config)
    instance.load_file(link, sheet)
    result = instance.read_last_row()
    return Result(data=result)


async def new_sheet(link, sheet, value):
    if not link or not sheet:
        return Result(error="Missing `link` or `sheet` value")
    instance = models.GoogleSheetInterface(**config)
    result = instance.create_new_sheet(link, sheet, value)
    return Result(data=result)


async def edit_sheet(link, sheet, value):
    if not link or not sheet:
        return Result(error="Missing `link` or `sheet` value")
    instance = models.GoogleSheetInterface(**config)
    result = instance.edit_sheet(link, sheet, value)
    return Result(data=result)


async def add_to_sheet(link, sheet, value):
    if not link or not sheet:
        return Result(error="Missing `link` or `sheet` value")
    instance = models.GoogleSheetInterface(**config)
    instance.load_file(link, sheet)
    key, value = instance.update_records(value)
    return await read_row(link, sheet, key, value[key])


async def fetch_groups(link, sheet, segments):
    if not link or not sheet:
        return Result(error="Missing `link` or `sheet` value")
    instance = models.GoogleSheetInterface(**config)
    instance.load_file(link, sheet)
    result = instance.fetch_groups(segments)
    return Result(data=result)


async def read_sheetnames(link) -> Result:
    if not link:
        return Result(error="Missing `link` or `sheet` value")
    instance = models.GoogleSheetInterface(**config)
    result = instance.get_sheet_names(link)
    title = instance.get_spreadsheet_title(link)
    return Result(data=dict(title=title, sheet_names=result))


async def read_new_row(link, sheet, page, page_size, key, value) -> Result:
    if not link or not sheet:
        return Result(error="Missing `link` or `sheet` value")
    instance = models.GoogleSheetInterface(**config)
    instance.load_file(link, sheet)
    full_result = instance.get_all_records()
    result = models.get_page(full_result, page_size=page_size, page=page)
    if value:
        if not key:
            return Result(error="Missing `key` field to read a single record")
        found = [x for x in result if x[key] == value]
        if found:
            return Result(data=found[0])
    return Result(data=result)


async def read_referenced_cell(link, sheet, options, key, value) -> Result:
    if not link or not sheet:
        return Result(error="Missing `link` or `sheet` value")
    instance = models.GoogleSheetInterface(**config)
    instance.load_file(link, sheet)
    result = instance.get_referenced_cell_values(options)
    if value:
        if not key:
            return Result(error="Missing `key` field to read a single record")
        found = [x for x in result if x[key] == value]
        if found:
            return Result(data=found[0])
    return Result(data=result)