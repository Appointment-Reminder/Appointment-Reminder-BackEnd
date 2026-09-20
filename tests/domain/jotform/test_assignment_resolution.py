# tests/domain/jotform/test_assignment_resolution.py
import pytest

from app.adapters.sql_model_adapter.jotform.adapters.sql_model_jotform_repository_adapter import \
    SQLModelJotformRepositoryAdapter
from app.adapters.sql_model_adapter.jotform.models.jotform import (
    JotformFormAssignment as AssignmentSQL,
    JotformCredential as CredentialSQL,
    JotformForm as FormSQL,
)
from app.adapters.sql_model_adapter.business.models.business import Business as BusinessSQL
from app.adapters.sql_model_adapter.business.models.business_member import BusinessMember as BusinessMemberSQL
from app.adapters.sql_model_adapter.package.models.package_category import PackageCategory as PackageCategorySQL
from app.adapters.sql_model_adapter.user.models.user import User as UserSQL


@pytest.fixture
def adapter(db_session):
    return SQLModelJotformRepositoryAdapter(db=db_session)


def _create_dependencies(db_session):
    user = UserSQL(email="owner@test.com", name="Owner", hashed_password="x")
    db_session.add(user)
    db_session.flush()

    business = BusinessSQL(name="Test Biz", owner_id=user.id)
    db_session.add(business)
    db_session.flush()

    member = BusinessMemberSQL(business_id=business.id, user_id=user.id, role="owner")
    db_session.add(member)
    db_session.flush()

    credential = CredentialSQL(business_id=business.id, label="main", api_key="key")
    db_session.add(credential)
    db_session.flush()

    form = FormSQL(
        credential_id=credential.id,
        form_id="ext-form-1",
        name="Booking Form",
        url="https://form.jotform.com/ext-form-1",  # required column, was missing
        field_mapping=[],
    )
    db_session.add(form)
    db_session.flush()

    category = PackageCategorySQL(business_id=business.id, name="Lifestyle")
    db_session.add(category)
    db_session.flush()

    db_session.commit()

    return {
        "business_id": business.id,
        "member_id": member.id,
        "form_id": form.id,
        "category_id": category.id,
    }


def _create_assignment(db_session, form_id, category_id, member_id):
    row = AssignmentSQL(form_id=form_id, category_id=category_id, business_member_id=member_id)
    db_session.add(row)
    db_session.commit()
    return row


class TestGetAssignmentByFormAndCategory:
    def test_single_assignment_returned(self, adapter, db_session):
        deps = _create_dependencies(db_session)
        _create_assignment(db_session, form_id=deps["form_id"], category_id=deps["category_id"], member_id=deps["member_id"])

        result = adapter.get_assignment_by_form_and_category(form_id=deps["form_id"], category_id=deps["category_id"])
        assert result is not None
        assert result.business_member_id == deps["member_id"]

    def test_zero_assignments_returns_none(self, adapter, db_session):
        deps = _create_dependencies(db_session)
        result = adapter.get_assignment_by_form_and_category(form_id=deps["form_id"], category_id=deps["category_id"])
        assert result is None

    def test_multiple_assignments_returns_none(self, adapter, db_session):
        deps = _create_dependencies(db_session)

        second_user = UserSQL(email="second@test.com", name="Second Photographer", hashed_password="x")
        db_session.add(second_user)
        db_session.flush()

        second_member = BusinessMemberSQL(business_id=deps["business_id"], user_id=second_user.id, role="photographer")
        db_session.add(second_member)
        db_session.commit()

        _create_assignment(db_session, form_id=deps["form_id"], category_id=deps["category_id"],
                           member_id=deps["member_id"])
        _create_assignment(db_session, form_id=deps["form_id"], category_id=deps["category_id"],
                           member_id=second_member.id)

        result = adapter.get_assignment_by_form_and_category(form_id=deps["form_id"], category_id=deps["category_id"])
        assert result is None

    def test_other_form_category_combinations_dont_leak(self, adapter, db_session):
        deps = _create_dependencies(db_session)
        _create_assignment(db_session, form_id=deps["form_id"], category_id=deps["category_id"], member_id=deps["member_id"])

        result = adapter.get_assignment_by_form_and_category(form_id=deps["form_id"] + 9999, category_id=deps["category_id"])
        assert result is None