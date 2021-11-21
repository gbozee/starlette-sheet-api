import asyncio
from os import error
from gsheet_service.types import Result, get_provider_sheet
import requests

# Imports the Google Cloud client library
from google.cloud import language_v1


async def process_spell_check(**data):
    web_spell_check, similarity_check = await asyncio.gather(
        web_spell_check_api(**data), similarity_check_api(**data)
    )
    if web_spell_check.error or similarity_check.error:
        return Result(
            error={
                "spelling": web_spell_check.error,
                "similarity": similarity_check.error,
            }
        )
    return Result(
        data={"spelling": web_spell_check.data, "similarity": similarity_check.data}
    )


def get_errors(v, text):
    result = {
        "type": v["type"],
        "text": text[v["offset"] : v["offset"] + v["length"]],
        "message": v["message"],
    }
    return result


async def web_spell_check_api(**data) -> Result:
    config = data.pop("server_config", {})
    spell_check_config = config.get("spell_check") or {}
    url = spell_check_config.get("url")
    text = data.get("text")
    api_key = spell_check_config.get("api_key")
    if url and text and api_key:
        result = requests.get(
            url,
            params={
                "text": text,
                "lang": data.get("lang") or "en_US",
                "format": "json",
                "customerid": api_key,
                "cmd": "check",
            },
        )
        if result.status_code < 400:
            response = result.json()
            data = response["result"]
            flat = [get_errors(x, text) for o in data for x in o["matches"]]
            return Result(data=flat)
        return Result(error="Error from processing check.")
    return Result(error="Missing url, text or api_key")


async def loop_helper(callback):
    loop = asyncio.get_event_loop()
    future = loop.run_in_executor(None, callback)
    return await future


async def similarity_check_api(**data) -> Result:
    config = data.pop("server_config", {})
    similarity_config = config.get("similarity") or {}
    url = similarity_config.get("url")
    api_key = similarity_config.get("api_key")
    main_text = data.get("text")
    other_texts = data.get("other_texts") or []

    if url and api_key and main_text and other_texts:

        def callback(o):
            rr = requests.get(
                url,
                params={
                    "text1": o["text1"],
                    "text2": o["text2"],
                    "token": api_key,
                    "bow": "always",
                },
            )
            if rr.status_code < 400:
                return rr.json()
            rr.raise_for_status()

        results = await asyncio.gather(
            *[
                loop_helper(lambda: callback({"text1": main_text, "text2": x}))
                for x in other_texts
            ]
        )
        return Result(data=results)
    return Result(error="Missing url, main_text, other_text or api_key")


async def google_nlp(text: str):
    # Instantiates a client
    client = language_v1.LanguageServiceClient()

    document = language_v1.Document(
        content=text, type_=language_v1.Document.Type.PLAIN_TEXT
    )

    # Detects the sentiment of the text
    sentiment = client.analyze_sentiment(
        request={"document": document}
    ).document_sentiment
    return Result(
        data={
            "text": text,
            "sentiment": {"score": sentiment.score, "magnitude": sentiment.magnitude},
        }
    )
