# tests/domain/jotform/test_submission_field.py
from app.domain.Jotform.models.jotform_field_mapping import SUBMISSION_FIELDS, SUBMISSION_FIELD_KEYS


class TestSubmissionFieldRegistry:
    def test_contains_expected_keys(self):
        expected = {
            "appointment_date", "package", "client_name", "client_email",
            "privacy_opt_out", "client_source_location", "referral_source",
            "add_ons", "guest_count",
        }
        actual = {f.key for f in SUBMISSION_FIELDS}
        assert expected.issubset(actual)

    def test_no_duplicate_keys(self):
        keys = [f.key for f in SUBMISSION_FIELDS]
        assert len(keys) == len(set(keys))

    def test_required_fields_are_exactly_expected(self):
        required = {f.key for f in SUBMISSION_FIELDS if f.required}
        assert required == {"appointment_date", "package", "client_name", "client_email"}

    def test_submission_field_keys_matches_definitions(self):
        assert SUBMISSION_FIELD_KEYS == {f.key for f in SUBMISSION_FIELDS}