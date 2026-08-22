from typing import Optional, List

from sqlalchemy.orm import Session
from sqlmodel import select

from app.domain.package.models.package import Package
from app.domain.package.models.package_category_model import PackageCategory
from app.domain.package.port.package_repository_port import PackageRepositoryPort


class SQLModelPackageRepositoryAdapter(PackageRepositoryPort):

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_package(self, package: Package) -> Package:
        package.jotform_alias = "test"
        self.db.add(package)
        self.db.commit()
        self.db.refresh(package)
        return package

    def update_package(self, package: Package) -> Package:
        existing = self.db.get(Package, package.id)
        if not existing:
            return None
        for key, value in package.dict(exclude_unset=True).items():
            setattr(existing, key, value)
        self.db.commit()
        self.db.refresh(existing)
        return existing

    def delete_package(self, package_id: int) -> bool:
        package = self.db.get(Package, package_id)
        if not package:
            return False
        self.db.delete(package)
        self.db.commit()
        return True

    def get_package_by_id(self, package_id: int) -> Optional[Package]:
        package = self.db.get(Package, package_id)
        if not package:
            return None
        return package

    def get_packages_by_business_id(self, business_id: int, is_active: bool = True) -> Optional[List[Package]]:
        query = select(Package).where(Package.business_id == business_id)
        if is_active:
            query = query.where(Package.is_active == is_active)

        return self.db.exec(query).all()

    def get_by_category(self, category_id: int, is_active: bool = True) -> List[Package]:
        query = select(Package).where(Package.category_id == category_id)

        if is_active:
            query = query.where(Package.is_active == is_active)

        return self.db.exec(query).all()

    def create_package_category(self, package_category: PackageCategory) -> PackageCategory:
        self.db.add(package_category)
        self.db.commit()
        self.db.refresh(package_category)
        return package_category

    def delete_package_category(self, package_category_id: int) -> bool:
        package_category = self.db.get(PackageCategory, package_category_id)
        if not package_category:
            return False
        self.db.delete(package_category)
        self.db.commit()
        return True

    def update_package_category(self, package_category: PackageCategory) -> PackageCategory:
        existing = self.db.get(PackageCategory, package_category.id)
        if not existing:
            return None
        for key, value in package_category.dict(exclude_unset=True).items():
            setattr(existing, key, value)

        self.db.commit()
        self.db.refresh(existing)
        return existing

    def get_categories_by_business(self, business_id: int) -> List[PackageCategory]:
        return self.db.exec(
            select(PackageCategory)
            .where(PackageCategory.business_id == business_id)
        ).all()

    def find_package_by_alias(self, business_id: int, category_id: int, alias_raw_value: str) -> Package:
        result = self.db.exec(
            select(Package)
            .where(Package.business_id == business_id)
            .where(Package.category_id == category_id)
            .where(Package.jotform_alias == alias_raw_value.strip())
        ).first()

        return result

    def get_category_by_id(self, category_id: int) -> Optional[PackageCategory]:
        return self.db.get(PackageCategory, category_id)