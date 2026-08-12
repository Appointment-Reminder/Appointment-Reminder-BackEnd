import httpx

from app.services.jotform.models.jotform_models import JotformForm, JotformQuestion
from app.services.jotform.ports.jotform_port import JotformPort


class JotformClientAdapter(JotformPort):
    BASE_URL = "https://eu-api.jotform.com"
    api_key: str
    async def get_list_forms(self, api_key:str) -> list[JotformForm]:
        r = httpx.get(f"{self.BASE_URL}/user/forms", params={"apiKey": api_key})
        r.raise_for_status()
        return [JotformForm(**f) for f in r.json()["content"]]

    async def get_form_questions(self, form_id: str, api_key:str) -> list[JotformQuestion]:
        r = httpx.get(f"{self.BASE_URL}/form/{form_id}/questions", params={"apiKey": api_key})
        r.raise_for_status()
        return [JotformQuestion(**q) for q in r.json()["content"].values()]

    async def register_webhook(self, form_id: str, url: str, api_key:str) -> None:
        return await super().register_webhook(form_id, url, api_key=api_key)



