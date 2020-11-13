import typing
import json
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2.rfc6749.errors import CustomOAuth2Error
from gsheet_service import settings, models, email_providers


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


async def get_provider_sheet(
    link=None, sheet=None, provider=None, key="client", **kwargs
):
    updated_config = {**config, **kwargs}
    instance = models.GoogleSheetInterface(**updated_config)
    instance.load_file(link, sheet)
    result = instance.get_all_records()
    if key:
        found = [x for x in result if x[key].lower() == provider.lower()]
        if found:
            return found[0]
    return None


def oauth_implementation(
    provider_instance, client_id=None, client_secret=None, **kwargs
):
    if "scopes" in kwargs:
        provider_instance["scopes"] = kwargs.pop("scopes")
    if "base_url" in kwargs:
        provider_instance["base_url"] = kwargs.pop("base_url")
    if "redirect_uri" in kwargs:
        provider_instance["redirect_uri"] = kwargs.pop("redirect_uri")
    if "token" in kwargs:
        provider_instance["token"] = kwargs.pop("token")
    base_url = provider_instance.get("base_url")
    scopes = provider_instance.get("scopes")
    redirect_uri = provider_instance.get("redirect_uri")
    token = provider_instance.get("token")
    if token:
        auto_refresh_url = (
            f"{provider_instance['base_url']}{provider_instance['token_path']}"
        )
        auto_refresh_kwargs = {"client_id": client_id, "client_secret": client_secret}
        new_token = None

        oauth = OAuth2Session(
            client_id=client_id,
            token=token,
            auto_refresh_url=auto_refresh_url,
            auto_refresh_kwargs=auto_refresh_kwargs,
            token_updater=lambda x: None,
        )
        new_token = oauth.refresh_token(auto_refresh_url, **auto_refresh_kwargs)
        return oauth, new_token
    else:
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
    additional_params = {}
    if "path" in kwargs:
        provider_instance["authorization_url_path"] = kwargs["path"]
    if "prompt" in kwargs:
        if provider_instance["client"] == "zoho":
            provider_instance["prompt"] = kwargs["prompt"]
    if "approval_prompt" in kwargs:
        if provider_instance["client"] == "gmail":
            provider_instance["approval_prompt"] = kwargs["approval_prompt"]
    if "access_type" in kwargs:
        provider_instance["access_type"] = kwargs["access_type"]
    if provider_instance.get('approval_prompt'):
        additional_params["approval_prompt"] = provider_instance["approval_prompt"]
    if provider_instance.get('prompt'):
        additional_params["prompt"] = provider_instance["prompt"]
    if provider_instance.get('access_type'):
        additional_params["access_type"] = provider_instance["access_type"]
    authorization_url, state = oauth_library.authorization_url(
        f"{provider_instance['base_url']}{provider_instance['authorization_url_path']}",
        **additional_params,
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
    string = authorization_response
    if settings.DEBUG:
        if (
            "localhost" in authorization_response.lower()
            or "127.0.0.1" in authorization_response.lower()
        ):
            string = string.replace("http://", "https://")

    token = oauth_library.fetch_token(
        full_url, authorization_response=string, client_secret=client_secret,
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


async def get_refresh_token(
    provider,
    link=None,
    sheet=None,
    refresh_token=None,
    key="client",
    credentials=None,
    with_provider_instance=False,
    **kwargs,
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
    client_secret = provider_instance.get("client_secret")
    if "client_secret" in kwargs:
        client_secret = kwargs.pop("client_secret")
    if not client_secret:
        return Result(error="client_secret not provided")
    if not refresh_token:
        return Result(error="No refresh token passed")
    _, new_token = oauth_implementation(
        provider_instance,
        client_id=client_id,
        client_secret=client_secret,
        token={"refresh_token": refresh_token},
        **kwargs,
    )
    if with_provider_instance:
        return new_token, provider_instance
    return Result(data=new_token)


async def get_emails(
    provider, search_config=None, key="client", **kwargs,
):
    generated_token, provider_instance = await get_refresh_token(
        provider, key=key, with_provider_instance=True, **kwargs
    )
    klass_options = {
        "zoho": email_providers.ZohoProvider,
        "gmail": email_providers.GmailProvider,
    }
    instance = klass_options[provider](generated_token, provider_instance)
    try:
        emails = await instance.get_emails(search_config)
        return Result(
            data={"emails": emails, "refresh_token": generated_token["refresh_token"]}
        )
    except Exception as e:
        print(e)
        return Result(error="Error fetching emails")


async def get_email_content(provider, email_data=None, key="client", **kwargs):
    generated_token, provider_instance = await get_refresh_token(
        provider, key=key, with_provider_instance=True, **kwargs
    )
    klass_options = {
        "zoho": email_providers.ZohoProvider,
        "gmail": email_providers.GmailProvider,
    }
    instance = klass_options[provider](generated_token, provider_instance)
    try:
        email_params = email_data or {}
        data = await instance.get_email_content(**email_params)
        return Result(
            data={"content": data, "refresh_token": generated_token["refresh_token"]}
        )
    except Exception as e:
        print(e)
        return Result(error="Error fetching email content")
