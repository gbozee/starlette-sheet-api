import asyncio
from requests_oauthlib import OAuth2Session
import requests


class EmailProvider:
    def __init__(self, token: dict, provider_instance):
        self.token = token
        self.provider_instance = provider_instance

    def headers(self):
        return {"Authorization": f"{self.auth_header} {self.token['access_token']}"}

    async def get_account_info(self):
        result = requests.get(f"{self.base_url}{self.me}", headers=self.headers(),)
        if result.status_code < 400:
            return self.parse_info(result.json())
        result.raise_for_status()

    def parse_info(self, response):
        raise NotImplementedError


class ZohoProvider(EmailProvider):
    provider = "zoho"
    base_url = "http://mail.zoho.com/api"
    me = "/accounts"
    auth_header = "Zoho-oauthtoken"

    def email_url(self, accountId):
        return self.base_url + f"/accounts/{accountId}/messages/search"

    def parse_info(self, response):
        return response["data"][0]

    async def get_emails(self, search_config, **kwargs):
        account_info = await self.get_account_info()
        parsed_config = self.parse_search_config(search_config or {})
        params = {"limit": 100, "searchKey": parsed_config}
        # import pdb; pdb.set_trace()
        result = requests.get(
            self.email_url(account_info["accountId"]),
            headers=self.headers(),
            params=params,
        )
        if result.status_code < 400:
            return result.json()["data"]
        result.raise_for_status()

    async def get_email_content(self, messageId="", folderId="", **kwargs):
        account_info = await self.get_account_info()
        result = requests.get(
            f"{self.base_url}/accounts/{account_info['accountId']}/folders/{folderId}/messages/{messageId}/content",
            headers=self.headers(),
        )
        if result.status_code < 400:
            return result.json()["data"]
        result.raise_for_status()

    def parse_search_config(self, config):
        result = ""
        if "sender" in config:
            individual = "::".join([f"sender:{x}" for x in config["sender"].split(",")])
            result = f"{result}{individual}"
        if "subject" in config:
            individual = "::".join(
                [f"subject:{x}" for x in config["subject"].split(" ")]
            )
            if result:
                result = f"{result}::"
            result = f"{result}{individual}"
        if "from" in config:
            result = f"{result}::fromDate:{config['from']}"
        if "to" in config:
            result = f"{result}::toDate:{config['to']}"
        if result:
            result = f"{result}::inclspamtrash:true"
        return result


class GmailProvider(EmailProvider):
    provider = "gmail"
    pass
