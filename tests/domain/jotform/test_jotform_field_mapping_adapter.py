# tests/domain/jotform/test_jotform_field_mapping_adapter.py
import pytest

from app.adapters.sql_model_adapter.jotform.adapters.sql_model_jotform_repository_adapter import \
    SQLModelJotformRepositoryAdapter
from app.adapters.sql_model_adapter.jotform.models.jotform import (
    JotformCredential as CredentialSQL,
    JotformForm as FormSQL,
)
from app.adapters.sql_model_adapter.business.models.business import Business as BusinessSQL
from app.adapters.sql_model_adapter.user.models.user import User as UserSQL
from app.domain.Jotform.models.jotform_field_mapping import JotformFieldMapping


@pytest.fixture
def adapter(db_session):
    return SQLModelJotformRepositoryAdapter(db=db_session)


def _create_form(db_session, form_id_str="ext-form-1", email=None, credential_id=None):
    """Builds the minimal parent chain and returns the real form.id.
    Pass credential_id to attach a second form to an existing business/credential."""
    if credential_id is None:
        user = UserSQL(email=email or f"owner-{form_id_str}@test.com", name="Owner", hashed_password="x")
        db_session.add(user)
        db_session.flush()

        business = BusinessSQL(name="Test Biz", owner_id=user.id)
        db_session.add(business)
        db_session.flush()

        credential = CredentialSQL(business_id=business.id, label="main", api_key="key")
        db_session.add(credential)
        db_session.flush()
        credential_id = credential.id

    form = FormSQL(
        credential_id=credential_id,
        form_id=form_id_str,
        name="Booking Form",
        url="https://form.jotform.com/" + form_id_str,
        field_mapping=[],
    )
    db_session.add(form)
    db_session.commit()
    db_session.refresh(form)

    return form.id


class TestSetFieldMappings:
    def test_full_replace_deletes_old_rows(self, adapter, db_session):
        form_id = _create_form(db_session)

        first = [JotformFieldMapping(form_id=form_id, target_key="client_name", qid="1", priority=0)]
        adapter.set_field_mappings(form_id, first)

        second = [JotformFieldMapping(form_id=form_id, target_key="client_name", qid="2", priority=0)]
        adapter.set_field_mappings(form_id, second)

        stored = adapter.get_field_mappings(form_id)
        assert len(stored) == 1
        assert stored[0].qid == "2"

    def test_empty_list_clears_all_mappings(self, adapter, db_session):
        form_id = _create_form(db_session)
        adapter.set_field_mappings(form_id, [JotformFieldMapping(form_id=form_id, target_key="client_name", qid="1", priority=0)])
        adapter.set_field_mappings(form_id, [])
        assert adapter.get_field_mappings(form_id) == []

    def test_other_forms_untouched(self, adapter, db_session):
        form_id_a = _create_form(db_session, "ext-form-a")
        form_id_b = _create_form(db_session, "ext-form-b")

        adapter.set_field_mappings(form_id_a, [JotformFieldMapping(form_id=form_id_a, target_key="client_name", qid="1", priority=0)])
        adapter.set_field_mappings(form_id_b, [JotformFieldMapping(form_id=form_id_b, target_key="client_name", qid="9", priority=0)])

        adapter.set_field_mappings(form_id_a, [])  # clear form A only

        assert adapter.get_field_mappings(form_id_a) == []
        assert len(adapter.get_field_mappings(form_id_b)) == 1

    def test_returns_rows_ordered_by_target_key_then_priority(self, adapter, db_session):
        form_id = _create_form(db_session)
        mappings = [
            JotformFieldMapping(form_id=form_id, target_key="package", qid="5", priority=0),
            JotformFieldMapping(form_id=form_id, target_key="client_name", qid="2", priority=1),
            JotformFieldMapping(form_id=form_id, target_key="client_name", qid="1", priority=0),
        ]
        adapter.set_field_mappings(form_id, mappings)
        result = adapter.get_field_mappings(form_id)

        keys_priorities = [(m.target_key, m.priority) for m in result]
        assert keys_priorities == sorted(keys_priorities)


class TestGetMappingByQid:
    def test_finds_existing_row(self, adapter, db_session):
        form_id = _create_form(db_session)
        adapter.set_field_mappings(form_id, [JotformFieldMapping(form_id=form_id, target_key="client_name", qid="7", priority=0)])
        result = adapter.get_mapping_by_qid(form_id, "7")
        assert result is not None
        assert result.qid == "7"

    def test_returns_none_when_absent(self, adapter, db_session):
        form_id = _create_form(db_session)
        assert adapter.get_mapping_by_qid(form_id, "999") is None