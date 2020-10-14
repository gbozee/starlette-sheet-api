import typing
import json
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2.rfc6749.errors import CustomOAuth2Error
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


async def get_provider_sheet(link, sheet, provider, key="client", **kwargs):
    updated_config = {**config, **kwargs}
    instance = models.GoogleSheetInterface(**updated_config)
    instance.load_file(link, sheet)
    result = instance.get_all_records()
    if key:
        found = [x for x in result if x[key].lower() == provider.lower()]
        if found:
            return found[0]
    return None


def oauth_implementation(provider_instance, client_id=None, **kwargs):
    if "scopes" in kwargs:
        provider_instance["scopes"] = kwargs.pop("scopes")
    if "base_url" in kwargs:
        provider_instance["base_url"] = kwargs.pop("base_url")
    if "redirect_uri" in kwargs:
        provider_instance["redirect_uri"] = kwargs.pop("redirect_uri")
    base_url = provider_instance.get("base_url")
    scopes = provider_instance.get("scopes")
    redirect_uri = provider_instance.get("redirect_uri")
    if all([client_id, base_url, scopes]):
        oauth = OAuth2Session(
            client_id=client_id,
            scope=scopes.split(","),
            redirect_uri=redirect_uri,
            state=provider_instance.get("state"),
        )
        return oauth
    return None


def resolve_authorization_url(
    oauth_library: OAuth2Session, provider_instance, **kwargs
):
    if "path" in kwargs:
        provider_instance["authorization_url_path"] = kwargs["path"]
    if "prompt" in kwargs:
        provider_instance["prompt"] = kwargs["prompt"]
    if "access_type" in kwargs:
        provider_instance["access_type"] = kwargs["access_type"]
    authorization_url, state = oauth_library.authorization_url(
        f"{provider_instance['base_url']}{provider_instance['authorization_url_path']}",
        prompt=provider_instance.get("prompt"),
        access_type=provider_instance.get("access_type"),
    )
    return authorization_url


def resolve_token(
    oauth_library: OAuth2Session,
    provider_instance,
    authorization_response,
    client_secret,
    **kwargs,
):
    if "path" in kwargs:
        provider_instance["token_path"] = kwargs["path"]
    full_url = f"{provider_instance['base_url']}{provider_instance['token_path']}"
    token = oauth_library.fetch_token(
        full_url,
        authorization_response=authorization_response,
        client_secret=client_secret,
    )
    return token


async def get_access_and_refresh_token(
    provider, link=None, sheet=None, key="client", credentials=None, **kwargs
):
    custom_credentials = {}
    if credentials:
        custom_credentials = credentials
    provider_instance = await get_provider_sheet(
        link, sheet, provider, key=key, **custom_credentials
    )
    if not provider_instance:
        return Result(error="Could not find provider in link provided")
    client_id = provider_instance.get("client_id")
    if "client_id" in kwargs:
        client_id = kwargs.pop("client_id")
    if not client_id:
        return Result(error="client_id not provided")

    oauth_library = oauth_implementation(
        provider_instance, client_id=client_id, **kwargs
    )
    if not oauth_library:
        return Result(error="Could not generate authorization url for provider passed")
    authorization_response = kwargs.pop("authorization_response", None)
    if not authorization_response:
        return Result(error="No authorization_response passed")
    client_secret = provider_instance.get("client_secret")
    if "client_secret" in kwargs:
        client_secret = kwargs.pop("client_secret")
    if not client_secret:
        return Result(error="client_secret not provided")
    try:
        token = resolve_token(
            oauth_library,
            provider_instance,
            authorization_response=authorization_response,
            client_secret=client_secret,
            **kwargs,
        )
        return Result(data=token)
    except CustomOAuth2Error as e:
        return Result(error="Error when trying to get token")


async def get_authorization_url(
    provider, link=None, sheet=None, key="client", credentials=None, **kwargs
):
    custom_credentials = {}
    if credentials:
        custom_credentials = credentials
    provider_instance = await get_provider_sheet(
        link, sheet, provider, key=key, **custom_credentials
    )
    if not provider_instance:
        return Result(error="Could not find provider in link provided")
    client_id = provider_instance.get("client_id")
    if "client_id" in kwargs:
        client_id = kwargs.pop("client_id")
    if not client_id:
        return Result(error="client_id not provided")
    oauth_library = oauth_implementation(
        provider_instance, client_id=client_id, **kwargs
    )
    if not oauth_library:
        return Result(error="Could not generate authorization url for provider passed")
    authorization_url = resolve_authorization_url(
        oauth_library, provider_instance, **kwargs
    )
    if not authorization_url:
        return Result(error="Could not generate authorization url for provider passed")
    return Result(data={"authorization_url": authorization_url})

