import asyncio
from requests_oauthlib import OAuth2Session
import requests
import json
import jwt
import base64


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
    base_url = "https://gmail.googleapis.com"
    auth_header = "Bearer"

    @property
    def account_id(self):
        decoded = jwt.decode(self.token["id_token"], verify=False)
        return decoded["sub"]

    def email_url(self, accountId):
        return self.base_url + f"/gmail/v1/users/{accountId}/messages"

    async def get_emails(self, search_config, **kwargs):
        parsed_config = self.parse_search_config(search_config or {})
        params = {"maxResults": 100, "q": parsed_config, "includeSpamTrash": "true"}
        result = requests.get(
            self.email_url(self.account_id), headers=self.headers(), params=params,
        )
        if result.status_code < 400:
            return result.json()["messages"]
        result.raise_for_status()

    def parse_search_config(self, config):
        result = ""
        if "sender" in config:
            #  OR from:GENS@gtbank.com
            individual = " ".join([f"from:{x}" for x in config["sender"].split(",")])
            result = result + "{" + individual + "}"
        if "subject" in config:
            individual = " ".join(
                [f'subject:("{x}")' for x in config["subject"].split(",")]
            )
            if result:
                result = f"{result} "
            result = result + "{" + individual + "}"
        if "from" in config:
            result = f"{result} after:{config['from']}"
        if "to" in config:
            result = f"{result}::before:{config['to']}"
        return result

    async def get_email_content(self, id="", threadId="", **kwargs):
        result = requests.get(
            f"{self.email_url(self.account_id)}/{id}", headers=self.headers(),
        )
        if result.status_code < 400:
            response = result.json()
            raw = response
            cleaned = self.clean_response(response)
            return raw
            # return {"raw": raw, "cleaned": json.dumps(cleaned)}
        result.raise_for_status()

    def clean_response(self, response):
        payload = response["payload"]
        headers = payload["headers"]
        content = payload["parts"]
        attributes = {x["name"]: x["value"] for x in headers}
        body = {
            x["mimeType"]: base64.urlsafe_b64decode(x["body"]["data"]) for x in content
        }
        return {
            **body,
            "subject": attributes.get("Subject"),
            "date": attributes.get("Date"),
            "from": attributes.get("From"),
            "received": attributes.get("Received"),
        }

