
import databases
import orm
import sqlalchemy

from .caches import RequestCache


def queryable(model, database, metadata, root=None):

    attributes = model.__dict__.copy()
    foreign_key_attributes = {
        key: value
        for key, value in attributes.items()
        if isinstance(value, orm.ForeignKey)
    }
    related_names = {}
    result = {}
    tables = []
    for key, value in foreign_key_attributes.items():
        value.to, _ = queryable(value.to, database, metadata)
        if value.related_name:
            related_names[value.to] = [value.related_name, key]
        tables.append(value.to)
        result[key] = value
    attributes.update({"__database__": database, "__metadata__": metadata, **result})
    # import ipdb; ipdb.set_trace()
    # import ipdb; ipdb.set_trace()
    NewModel = type(model.__name__, (orm.Model, *model.mro()), attributes)
    for value in tables:
        # dynamically create properties on the related models to fetch the records
        if value in related_names.keys():
            RelatedModel, field_name = related_names[value]
            setattr(
                value,
                RelatedModel,
                property(
                    lambda self: NewModel.objects.filter(
                        **{f"{field_name}__id": self.id}
                    )
                ),
            )
        # setattr(value, model.__name__, NewModel)
    return NewModel, tables


def init_tables(database_url, **kwargs):
    database = databases.Database(database_url, **kwargs)
    metadata = sqlalchemy.MetaData()
    return database, metadata


class ServiceAPI:
    def __init__(self, database_url, **kwargs):
        self.url = database_url
        self.database = databases.Database(database_url, **kwargs)
        self.metadata = sqlalchemy.MetaData()
        _Jobs, tables = self.get_model(RequestCache)
        self.RequestCache: RequestCache = _Jobs

    def get_model(self, model):
        return queryable(model, self.database, self.metadata)

    async def db_action(self, value="connect"):
        if value == "connect":
            await self.database.connect()
        else:
            await self.database.disconnect()

    async def get_record(self, request_id: str):
        result = await self.RequestCache.objects.filter(request_id=request_id).first()
        if result:
            return result.data
        return None

    async def update_record(self, request_id: str, data):
        # check if it exists if it does, update else create
        result = await self.RequestCache.objects.filter(request_id=request_id).first()
        if result:
            result.data = data
            await result.save()
        else:
            await self.RequestCache.objects.create(request_id=request_id, data=data)

# service = ServiceAPI(settings.DATABASE_URL)
