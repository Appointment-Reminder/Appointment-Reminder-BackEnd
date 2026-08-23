from typing import Optional, List

from sqlalchemy.orm import Session
from sqlmodel import select

from app.domain.package.models.package import Package as PackageEntity
from app.domain.package.models.package_category_model import PackageCategory as PackageCategoryEntity

from app.adapters.sql_model_adapter.package.models.package import Package as PackageSQL, _to_domain as package_to_domain, _apply_sql as package_apply_sql
from app.adapters.sql_model_adapter.package.models.package_category import PackageCategory as PackageCategorySQL, _to_domain as package_category_to_domain, _apply_sql as package_category_apply_sql

from app.domain.package.port.package_repository_port import PackageRepositoryPort


class SQLModelPackageRepositoryAdapter(PackageRepositoryPort):

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_package(self, package: PackageEntity) -> PackageEntity:
        sql_obj = PackageSQL(
            business_id=package.business_id,
            category_id=package.category_id,
            name=package.name,
            description=package.description,
            is_active=package.is_active,
            jotform_alias=package.jotform_alias,
        )
        self.db.add(sql_obj)
        self.db.commit()
        self.db.refresh(sql_obj)
        return package_to_domain(sql_obj)

    def update_package(self, package: PackageEntity) -> PackageEntity:
        existing = self.db.get(PackageSQL, package.id)
        if not existing:
            return None
        package_apply_sql(sql=existing, obj=package)
        self.db.commit()
        self.db.refresh(existing)
        return package_to_domain(existing)

    def delete_package(self, package_id: int) -> bool:
        package = self.db.get(PackageSQL, package_id)
        if not package:
            return False
        self.db.delete(package)
        self.db.commit()
        return True

    def get_package_by_id(self, package_id: int) -> Optional[PackageEntity]:
        package = self.db.get(PackageSQL, package_id)
        return package_to_domain(package) if package else None

    def get_packages_by_business_id(self, business_id: int, is_active: bool = True) -> Optional[List[PackageEntity]]:
        query = select(PackageSQL).where(PackageSQL.business_id == business_id)
        if is_active:
            query = query.where(PackageSQL.is_active == is_active)

        result = self.db.exec(query).all()
        return [package_to_domain(package) for package in result] if result else None

    def get_by_category(self, category_id: int, is_active: bool = True) -> List[PackageEntity]:
        query = select(PackageSQL).where(PackageSQL.category_id == category_id)

        if is_active:
            query = query.where(PackageSQL.is_active == is_active)

        result = self.db.exec(query).all()
        return [package_to_domain(package) for package in result] if result else None

    def create_package_category(self, package_category: PackageCategoryEntity) -> PackageCategoryEntity:
        sql_obj = PackageCategorySQL(
            business_id=package_category.business_id,
            name=package_category.name,
        )
        self.db.add(sql_obj)
        self.db.commit()
        self.db.refresh(sql_obj)
        return package_category_to_domain(sql_obj)

    def delete_package_category(self, package_category_id: int) -> bool:
        package_category = self.db.get(PackageCategorySQL, package_category_id)
        if not package_category:
            return False
        self.db.delete(package_category)
        self.db.commit()
        return True

    def update_package_category(self, package_category: PackageCategoryEntity) -> PackageCategoryEntity:
        existing = self.db.get(PackageCategorySQL, package_category.id)
        if not existing:
            return None

        package_category_apply_sql(sql=existing, obj=package_category)

        self.db.commit()
        self.db.refresh(existing)
        return package_category_to_domain(existing)

    def get_categories_by_business(self, business_id: int) -> List[PackageCategoryEntity]:
        result = self.db.exec(
            select(PackageCategorySQL)
            .where(PackageCategorySQL.business_id == business_id)
        ).all()
        return [package_category_to_domain(package_category) for package_category in result]

    def find_package_by_alias(self, business_id: int, category_id: int, alias_raw_value: str) -> PackageEntity:
        result = self.db.exec(
            select(PackageSQL)
            .where(PackageSQL.business_id == business_id)
            .where(PackageSQL.category_id == category_id)
            .where(PackageSQL.jotform_alias == alias_raw_value.strip())
        ).first()

        return package_category_to_domain(result) if result else None

    def get_category_by_id(self, category_id: int) -> Optional[PackageCategoryEntity]:
        result = self.db.get(PackageCategorySQL, category_id)
        return package_category_to_domain(result) if result else None