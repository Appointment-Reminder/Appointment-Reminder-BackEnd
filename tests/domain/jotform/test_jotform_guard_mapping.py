# tests/domain/jotform/test_jotform_guard_mapping.py
import pytest
from unittest.mock import Mock

from app.domain.Jotform.errors.jotform_errors import JotformDomainError
from app.domain.Jotform.guard.jotform_guard import JotformGuard
from app.domain.Jotform.models.jotform_field_mapping import JotformFieldMapping


@pytest.fixture
def jotform_repo():
    return Mock()

@pytest.fixture
def guard(jotform_repo):
    return JotformGuard(jotform_repo=jotform_repo)

def _mapping(target_key="client_name", qid="1", priority=0, subkey=None):
    return JotformFieldMapping(form_id=10, target_key=target_key, qid=qid, priority=priority, subkey=subkey)


class TestEnsureMappingValid:
    def test_passes_for_valid_target_keys(self, guard):
        mappings = [_mapping(target_key="client_name"), _mapping(target_key="package", qid="2")]
        guard.ensure_mapping_valid(mappings)  # no raise

    def test_raises_on_unknown_target_key(self, guard):
        mappings = [_mapping(target_key="not_a_real_field")]
        with pytest.raises(JotformDomainError):
            guard.ensure_mapping_valid(mappings)

    def test_empty_list_passes(self, guard):
        guard.ensure_mapping_valid([])


class TestEnsureNoDuplicateQid:
    def test_passes_for_distinct_qid_subkey_pairs(self, guard):
        mappings = [
            _mapping(qid="1", subkey="first", target_key="first_name", priority=0),
            _mapping(qid="1", subkey="last", target_key="last_name", priority=0),
        ]
        guard.ensure_no_duplicate_qid(mappings)  # no raise

    def test_raises_on_duplicate_qid_and_subkey(self, guard):
        mappings = [
            _mapping(target_key="client_name", qid="1", priority=0),
            _mapping(target_key="referral_source", qid="1", priority=0),
        ]
        with pytest.raises(JotformDomainError):
            guard.ensure_no_duplicate_qid(mappings)

    def test_raises_on_duplicate_target_key_and_priority(self, guard):
        mappings = [
            _mapping(target_key="client_name", qid="1", priority=0),
            _mapping(target_key="client_name", qid="2", priority=0),
        ]
        with pytest.raises(JotformDomainError):
            guard.ensure_no_duplicate_qid(mappings)

    def test_allows_same_qid_across_different_subkeys(self, guard):
        mappings = [
            _mapping(target_key="client_name", qid="3", subkey="first", priority=0),
            _mapping(target_key="client_name", qid="3", subkey="last", priority=1),
        ]
        guard.ensure_no_duplicate_qid(mappings)  # no raise