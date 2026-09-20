# tests/domain/package/test_find_package_by_submission_alias.py
import pytest

from app.adapters.sql_model_adapter.package.adapters.sql_model_package_repository_adapter import \
    SQLModelPackageRepositoryAdapter
from app.adapters.sql_model_adapter.package.models.package import Package as PackageSQL
from app.adapters.sql_model_adapter.package.models.package_category import PackageCategory as PackageCategorySQL
from app.adapters.sql_model_adapter.business.models.business import Business as BusinessSQL
from app.adapters.sql_model_adapter.user.models.user import User as UserSQL


@pytest.fixture
def adapter(db_session):
    return SQLModelPackageRepositoryAdapter(db=db_session)


def _create_business(db_session, email="owner@test.com"):
    user = UserSQL(email=email, name="Owner", hashed_password="x")
    db_session.add(user)
    db_session.flush()

    business = BusinessSQL(name="Test Biz", owner_id=user.id)
    db_session.add(business)
    db_session.commit()
    db_session.refresh(business)

    return business.id


def _create_category(db_session, business_id, name="Lifestyle"):
    category = PackageCategorySQL(business_id=business_id, name=name)
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category.id


def _create_package(db_session, business_id, category_id, alias, name="Pkg"):
    pkg = PackageSQL(
        business_id=business_id, category_id=category_id, name=name,
        description="d", is_active=True, jotform_alias=alias,
    )
    db_session.add(pkg)
    db_session.commit()
    db_session.refresh(pkg)
    return pkg


class TestFindPackageBySubmissionAlias:
    def test_exact_match_returns_package(self, adapter, db_session):
        business_id = _create_business(db_session)
        category_id = _create_category(db_session, business_id)
        _create_package(db_session, business_id=business_id, category_id=category_id, alias="Gold Package")

        result = adapter.find_package_by_submission_alias(business_id=business_id, alias_raw_value="Gold Package")
        assert result is not None
        assert result.jotform_alias == "Gold Package"

    def test_no_match_returns_none(self, adapter, db_session):
        business_id = _create_business(db_session)
        result = adapter.find_package_by_submission_alias(business_id=business_id, alias_raw_value="Nonexistent")
        assert result is None

    def test_multiple_matches_returns_none(self, adapter, db_session):
        business_id = _create_business(db_session)
        category_a = _create_category(db_session, business_id, name="Cat A")
        category_b = _create_category(db_session, business_id, name="Cat B")

        _create_package(db_session, business_id=business_id, category_id=category_a, alias="Dup", name="A")
        _create_package(db_session, business_id=business_id, category_id=category_b, alias="Dup", name="B")

        result = adapter.find_package_by_submission_alias(business_id=business_id, alias_raw_value="Dup")
        assert result is None

    def test_non_breaking_space_normalized_both_ways(self, adapter, db_session):
        business_id = _create_business(db_session)
        category_id = _create_category(db_session, business_id)
        _create_package(db_session, business_id=business_id, category_id=category_id, alias="PARISIAN DREAM\u00a012 HOURS")

        result = adapter.find_package_by_submission_alias(
            business_id=business_id, alias_raw_value="PARISIAN DREAM 12 HOURS"  # regular space incoming
        )
        assert result is not None

    def test_scoped_to_business_id(self, adapter, db_session):
        business_a = _create_business(db_session, email="owner-a@test.com")
        business_b = _create_business(db_session, email="owner-b@test.com")
        category_a = _create_category(db_session, business_a)

        _create_package(db_session, business_id=business_a, category_id=category_a, alias="Shared Name")

        result = adapter.find_package_by_submission_alias(business_id=business_b, alias_raw_value="Shared Name")
        assert result is None

    def test_trims_leading_trailing_whitespace(self, adapter, db_session):
        business_id = _create_business(db_session)
        category_id = _create_category(db_session, business_id)
        _create_package(db_session, business_id=business_id, category_id=category_id, alias="Gold Package")

        result = adapter.find_package_by_submission_alias(business_id=business_id, alias_raw_value="  Gold Package  ")
        assert result is not None


class TestPackageUpdatePersistsAlias:
    def test_jotform_alias_round_trips_through_update(self, adapter, db_session):
        from app.domain.package.models.package import Package as PackageEntity

        business_id = _create_business(db_session)
        category_id = _create_category(db_session, business_id)
        created = _create_package(db_session, business_id=business_id, category_id=category_id, alias="Old Alias")

        updated_entity = PackageEntity(
            id=created.id, business_id=business_id, category_id=category_id, name="Pkg",
            description="d", is_active=True, jotform_alias="New Alias",
        )
        result = adapter.update_package(updated_entity)

        assert result.jotform_alias == "New Alias"
        refetched = adapter.get_package_by_id(created.id)
        assert refetched.jotform_alias == "New Alias"