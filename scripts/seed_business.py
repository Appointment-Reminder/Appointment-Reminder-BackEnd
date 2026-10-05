# seed_business.py
from sqlmodel import Session, select
from datetime import datetime


from app.adapters.sql_model_adapter.business.models.business import Business
from app.adapters.sql_model_adapter.business.models.business_member import BusinessMember
from app.adapters.sql_model_adapter.user.models.user import User
from app.adapters.sql_model_adapter.appointment.models.appointment import Appointment
from app.adapters.sql_model_adapter.jotform.models.jotform import JotformCredential, JotformForm, JotformFormAssignment
from app.adapters.sql_model_adapter.jotform.models.jotform_field_mapping import JotformFieldMapping

from app.adapters.session import engine
from app.adapters.sql_model_adapter.business.models.member_commission import MemberCommission as MemberCommissionSQL
from app.adapters.sql_model_adapter.package.models.package import Package as PackageSQL
from app.adapters.sql_model_adapter.package.models.package_category import PackageCategory as PackageCategorySQL
from app.adapters.sql_model_adapter.package.models.package_price import PackagePrice as PackagePriceSQL

BUSINESS_ID = 7
CATEGORY_NAME = "Standard Sessions"  # single category, adjust if you split later
EFFECTIVE_FROM = datetime(2026, 1, 1)  # backdate before your earliest appointment

# business_members.id of the photographers earning a commission (the owner, Gabby Sy = 7, earns none)
JESSICA_MEMBER_ID = 8  # commission = the package's photographer share
PINHAS_MEMBER_ID = 9  # commission = price - deposit
CAROLINA_MEMBER_ID = 10  # commission = price - deposit

PACKAGES = [
    # name, price, photographer_share, duration, deposit
    ("A - 30 MINUTES", 180, 130, 30, 50),
    ("B - 1 HOUR", 230, 170, 60, 50),
    ("C - 1 HR 30 MINS", 280, 190, 90, 50),
    ("D - 2 HOURS", 350, 250, 120, 50),
    ("E - 2 HRS 30 MINS", 400, 280, 150, 50),
    ("F - 3 HOURS", 450, 310, 180, 50),
    ("SUNSET & NIGHT SESSION - 1", 300, 200, 60, 50),
    ("PARISIAN DREAM 12 HOURS (600 Edited) - €2000", 2000, 2000, 720, 100),
    ("L'AMOUR FOREVER 8 HOURS (500 Edited) - €1500", 1500, 1500, 480, 100),
    ("ROMANCE IN PARIS 5 HOURS (350 Edited) - €1000", 1000, 1000, 300, 100),
    ("TIMELESS MOMENTS 3 HOURS (250 Edited) - €800", 800, 800, 180, 100),
    ("PARIS ELEGANCE EXPRESS 2 HOURS (150 Edited) - €600", 600, 600, 120, 100),
    ("PARIS ESCAPE 1 HOUR (90 Edited) - €400", 400, 400, 60, 100),
    ("DISNEYLAND - 1 HR", 270, 270, 90, 50),
]

# packages whose photographer share is a placeholder, not a real split
CUSTOM_QUOTE_PACKAGES = {
    "PARISIAN DREAM 12 HOURS (600 Edited) - €2000",
    "L'AMOUR FOREVER 8 HOURS (500 Edited) - €1500",
    "ROMANCE IN PARIS 5 HOURS (350 Edited) - €1000",
    "TIMELESS MOMENTS 3 HOURS (250 Edited) - €800",
    "PARIS ELEGANCE EXPRESS 2 HOURS (150 Edited) - €600",
    "PARIS ESCAPE 1 HOUR (90 Edited) - €400",
}


def commissions_for(price: int, photographer_share: int, deposit: int) -> dict[int, int]:
    """Flat commission per member id. The owner's income is what is left: price - commission."""
    return {
        JESSICA_MEMBER_ID: photographer_share,
        PINHAS_MEMBER_ID: price - deposit,
        CAROLINA_MEMBER_ID: price - deposit,
    }


def get_or_create_category(db: Session) -> PackageCategorySQL:
    category = db.exec(
        select(PackageCategorySQL)
        .where(PackageCategorySQL.business_id == BUSINESS_ID)
        .where(PackageCategorySQL.name == CATEGORY_NAME)
    ).first()
    if category is None:
        category = PackageCategorySQL(business_id=BUSINESS_ID, name=CATEGORY_NAME)
        db.add(category)
        db.commit()
        db.refresh(category)
    return category


def get_or_create_package(db: Session, category_id: int, name: str, duration: int) -> PackageSQL:
    pkg = db.exec(
        select(PackageSQL)
        .where(PackageSQL.business_id == BUSINESS_ID)
        .where(PackageSQL.jotform_alias == name)
    ).first()
    if pkg is None:
        pkg = PackageSQL(business_id=BUSINESS_ID, jotform_alias=name)  # alias matches the jotform "Name" column
    pkg.category_id = category_id
    pkg.name = name
    pkg.description = "Custom quote — split not final" if name in CUSTOM_QUOTE_PACKAGES else ""
    pkg.is_active = True
    pkg.package_duration = duration
    db.add(pkg)
    db.commit()
    db.refresh(pkg)
    return pkg


def upsert_price(db: Session, package_id: int, price: int, deposit: int) -> None:
    row = db.exec(
        select(PackagePriceSQL)
        .where(PackagePriceSQL.package_id == package_id)
        .where(PackagePriceSQL.effective_from == EFFECTIVE_FROM)
    ).first() or PackagePriceSQL(package_id=package_id, effective_from=EFFECTIVE_FROM)
    row.total_price = price
    row.deposit_amount = deposit
    row.remaining_amount = price - deposit
    db.add(row)


def upsert_commission(db: Session, member_id: int, package_id: int, amount: int) -> None:
    row = db.exec(
        select(MemberCommissionSQL)
        .where(MemberCommissionSQL.business_member_id == member_id)
        .where(MemberCommissionSQL.package_id == package_id)
        .where(MemberCommissionSQL.effective_from == EFFECTIVE_FROM)
    ).first() or MemberCommissionSQL(
        business_member_id=member_id, package_id=package_id, effective_from=EFFECTIVE_FROM,
        commission_amount=0, commission_isPercentage=False,
    )
    row.commission_amount = amount
    row.commission_isPercentage = False  # flat amount
    db.add(row)


def main():
    with Session(engine) as db:
        category = get_or_create_category(db)

        name_to_package_id = {}

        for name, price, photog_share, duration, deposit in PACKAGES:
            pkg = get_or_create_package(db, category.id, name, duration)
            name_to_package_id[name] = pkg.id

            upsert_price(db, pkg.id, price, deposit)
            for member_id, amount in commissions_for(price, photog_share, deposit).items():
                upsert_commission(db, member_id, pkg.id, amount)
            db.commit()

        print(name_to_package_id)  # paste this dict into the appointment import script


if __name__ == "__main__":
    main()
