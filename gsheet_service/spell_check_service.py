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


async def google_nlp(**data):
    content = data.get("text")
    if not content:
        return Result(error={"msg": "Missing text"})
    client = language_v1.LanguageServiceClient()
    encoding_type = language_v1.EncodingType.UTF8
    document = language_v1.Document(
        content=content, type_=language_v1.Document.Type.PLAIN_TEXT
    )
    result = {}
    response = client.analyze_entities(
        request={"document": document, "encoding_type": encoding_type},
    )
    entities = []
    for entity in response.entities:
        sentiment = entity.sentiment
        entities.append(
            {
                "name": entity.name,
                "type": language_v1.Entity.Type(entity.type_).name,
                "salience_score": entity.salience,
                "sentiment": {
                    "score": sentiment.score,
                    "magnitude": sentiment.magnitude,
                },
                "metadata": [
                    {"name": x[0], "value": x[1]} for x in entity.metadata.items()
                ],
                "mention": [
                    {
                        "text": x.text.content,
                        "type": language_v1.EntityMention.Type(x.type_).name,
                    }
                    for x in entity.mentions
                ],
            }
        )
    result["entities"] = entities
    response = client.analyze_sentiment(
        request={"document": document, "encoding_type": encoding_type}
    )
    sentiment = {
        "score": response.document_sentiment.score,
        "magnitude": response.document_sentiment.magnitude,
        "sentences": [
            {
                "text": x.text.content,
                "score": x.sentiment.score,
                "magnitude": x.sentiment.magnitude,
            }
            for x in response.sentences
        ],
    }
    result["sentiment"] = sentiment
    response = client.analyze_syntax(
        request={"document": document, "encoding_type": encoding_type}
    )
    tokens = []
    for token in response.tokens:
        text = token.text
        part_of_speech = token.part_of_speech
        dependency_edge = token.dependency_edge
        tokens.append(
            {
                "text": text.content,
                "location": text.begin_offset,
                "part_of_speech": language_v1.PartOfSpeech.Tag(part_of_speech.tag).name,
                "voice": language_v1.PartOfSpeech.Voice(part_of_speech.voice).name,
                "tense": language_v1.PartOfSpeech.Tense(part_of_speech.tense).name,
                "lemma": token.lemma,
                "head_token_index": dependency_edge.head_token_index,
                "label": language_v1.DependencyEdge.Label(dependency_edge.label).name,
            }
        )
    result["tokens"] = tokens
    response = client.classify_text(request={"document": document})
    categories = []
    for category in response.categories:
        categories.append({"name": category.name, "confidence": category.confidence})
    result["categories"] = categories

    # Detects the sentiment of the text
    return Result(data=result)
