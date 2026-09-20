# tests/adapters/jotform/test_api_jotform_port_questions.py
import pytest
from unittest.mock import AsyncMock, patch, Mock

from app.adapters.jotform.APIJotformPort import JotformClientAdapter


# Trimmed subset of the real captured form payload (see conversation doc 130) —
# enough to exercise the filtering + parsing logic without needing an external file.
REAL_FORM_CONTENT_SAMPLE = {
    "1": {"qid": "1", "text": "Reserve Your Lifestyle & Travel Photoshoot Session", "type": "control_head"},
    "3": {"qid": "3", "text": "Name", "type": "control_fullname"},
    "5": {"qid": "5", "text": "Mobile Number", "type": "control_phone"},
    "8": {"qid": "8", "text": "By signing below...", "type": "control_widget"},
    "27": {"qid": "27", "text": "Submit", "type": "control_button"},
    "69": {"qid": "69", "text": "Email", "type": "control_email"},
    "81": {"qid": "81", "text": "Important: Payment must be completed...", "type": "control_text"},
    "175": {"qid": "175", "text": "Divider", "type": "control_divider"},
    "220": {"qid": "220", "text": "Full Legal Terms Below", "type": "control_collapse"},
    "163": {
        "qid": "163", "text": "Number Of People In The Session", "type": "control_dropdown",
        "options": "1|2|3|4|5 - MAX GROUP SIZE FOR PACKAGES A/B/C|6 - MAX GROUP SIZE FOR PACKAGES D/E/F",
    },
    "65": {"qid": "65", "text": "A - 30 MINUTES €180 (1 Location)(40 Edited)(Includes Up To 5 People)", "type": "control_appointment"},
}


@pytest.fixture
def adapter():
    return JotformClientAdapter()


def _mock_response(json_body):
    resp = Mock()
    resp.raise_for_status = Mock()
    resp.json = Mock(return_value=json_body)
    return resp


class TestGetFormQuestionsAgainstRealSample:
    @pytest.mark.asyncio
    async def test_known_qids_present_and_correct(self, adapter):
        with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=_mock_response({"content": REAL_FORM_CONTENT_SAMPLE}))):
            result = await adapter.get_form_questions("form-1", "key")
            by_id = {q.id: q for q in result}

            assert "3" in by_id and by_id["3"].name == "Name"
            assert "69" in by_id and by_id["69"].name == "Email"
            assert "163" in by_id
            assert len(by_id["163"].options) == 6

    @pytest.mark.asyncio
    async def test_layout_and_policy_noise_filtered_out(self, adapter):
        with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=_mock_response({"content": REAL_FORM_CONTENT_SAMPLE}))):
            result = await adapter.get_form_questions("form-1", "key")
            by_id = {q.id: q for q in result}

            assert "1" not in by_id    # control_head
            assert "27" not in by_id   # control_button
            assert "81" not in by_id   # control_text
            assert "175" not in by_id  # control_divider
            assert "220" not in by_id  # control_collapse
            assert "8" not in by_id    # control_widget