# tests/test_jotform_api_adapter.py
# NOTE: written against the CURRENT adapter code — these will fail
# until you fix the httpx.AsyncClient usage (instantiate a client,
# don't call .get as a staticmethod) and drop the `super().register_webhook`
# call (Protocol has no base implementation).
import pytest
import respx
import httpx

from app.adapters.jotform.APIJotformPort import JotformClientAdapter


@pytest.mark.asyncio
@respx.mock
async def test_get_list_forms_parses_response():
    respx.get("https://eu-api.jotform.com/user/forms").mock(
        return_value=httpx.Response(200, json={"content": [
            {"id": 1, "name": "Wedding Form", "title": "Wedding Form", "status": 'available', "url": "testurl"},
        ]})
    )
    adapter = JotformClientAdapter()

    forms = await adapter.get_list_forms(api_key="fake-key")

    assert forms[0].name == "Wedding Form"


@pytest.mark.asyncio
@respx.mock
async def test_get_form_questions_parses_response():
    respx.get("https://eu-api.jotform.com/form/123/questions").mock(
        return_value=httpx.Response(200, json={"content": {
            "1": {"qid": 1, "text": "email", "type":"test", "options": []},
        }})
    )
    adapter = JotformClientAdapter()

    questions = await adapter.get_form_questions(form_id="123", api_key="fake-key")

    assert questions[0].name == "email"