import httpx

from app.domain.Jotform.models.jotform_form_model import JotformForm, JotformQuestion
from app.domain.Jotform.port.jotform_port import JotformPort


class JotformClientAdapter(JotformPort):
    BASE_URL = "https://eu-api.jotform.com"

    async def get_list_forms(self, api_key:str) -> list[JotformForm]:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.BASE_URL}/user/forms", params={"apiKey": api_key})
        r.raise_for_status()
        print(r.json()["content"])
        return [self._to_remote_form(f) for f in r.json()["content"]]

    async def get_form_questions(self, form_id: str, api_key:str) -> list[JotformQuestion]:
        r = httpx.AsyncClient.get(f"{self.BASE_URL}/form/{form_id}/questions", params={"apiKey": api_key})
        r.raise_for_status()
        return [JotformQuestion(**q) for q in r.json()["content"].values()]

    async def register_webhook(self, form_id: str, url: str, api_key:str) -> None:
        return await super().register_webhook(form_id, url, api_key=api_key)

    def _to_remote_form(self, raw:dict) -> JotformForm:
        return JotformForm(
            form_id=raw["id"],
            name=raw["title"],
            status=raw["status"],
            url=raw["url"],
        )



