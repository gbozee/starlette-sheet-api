import datetime
import logging

import orm

logging.basicConfig(level=logging.INFO)


class BotMixin(object):
    pass


def new_timezone():
    uu = datetime.datetime.now()
    return uu


class RequestCache(object):
    __tablename__ = "sheet_request_cache"
    id = orm.Integer(primary_key=True)
    request_id = orm.Text()
    data = orm.JSON(default={})
