# tests/domain/jotform/test_jotform_webhook_parser.py
import json
import pytest
from pathlib import Path

from app.domain.Jotform.service.jotform_webhook_parser import parse_jotform_raw_request


@pytest.fixture
def raw_request():
    path = Path(__file__).parents[3] / "tests" / "webhook.json"
    return json.loads(path.read_text(encoding="utf-8"))

@pytest.fixture
def parsed(raw_request):
    return parse_jotform_raw_request(raw_request)


class TestPlainScalarFields:
    def test_email(self, parsed):
        assert parsed["69"]["answer"] == "john@example.com"

    def test_package_choice(self, parsed):
        assert parsed["123"]["answer"] == "PARISIAN DREAM\u00a012 HOURS (600 Edited) - \u20ac2000"

    def test_how_did_you_find_us(self, parsed):
        assert parsed["164"]["answer"] == "Les Frenchies Paris Travel Tips Facebook Group"


class TestCompositeFields:
    def test_name_splits_first_last(self, parsed):
        assert parsed["3"]["answer"] == {"first": "John", "last": "Smith"}

    def test_phone_number_composite(self, parsed):
        assert parsed["5"]["answer"] == {"area": "312", "phone": "312"}

    def test_appointment_date_composite(self, parsed):
        answer = parsed["65"]["answer"]
        assert answer["date"] == "2026-07-31 11:00"
        assert answer["duration"] == "30"


class TestListFields:
    def test_stay_connected_is_list(self, parsed):
        assert parsed["93"]["answer"] == ["I will have mobile data (not relying on Wi-Fi)."]

    def test_additional_services_is_list(self, parsed):
        assert parsed["94"]["answer"] == ["Personal Assistant Only \u2013 \u20ac40 per hour"]


class TestNonQuestionKeysIgnored:
    @pytest.mark.parametrize("metadata_key", [
        "slug", "jsExecutionTracker", "submitSource", "submitDate", "buildDate",
        "uploadServerUrl", "eventObserver", "eventObserverPayment", "timeToSubmit",
        "preview", "validatedNewRequiredFieldIDs", "path",
    ])
    def test_metadata_key_absent(self, parsed, metadata_key):
        assert metadata_key not in parsed

    def test_appointment_slot_helper_does_not_clobber_real_answer(self, parsed):
        assert parsed["65"]["answer"]["date"] == "2026-07-31 11:00"

    def test_only_numeric_qids_present(self, parsed):
        for qid in parsed:
            assert qid.isdigit()


class TestSignatureField:
    def test_signature_data_uri_preserved(self, parsed):
        assert parsed["8"]["answer"].startswith("data:image/png;base64,")