# seed_packages.py
from sqlmodel import Session
from datetime import datetime


from app.adapters.sql_model_adapter.business.models.business import Business
from app.adapters.sql_model_adapter.business.models.business_member import BusinessMember
from app.adapters.sql_model_adapter.business.models.member_commission import MemberCommission
from app.adapters.sql_model_adapter.user.models.user import User
from app.adapters.sql_model_adapter.package.models.package import Package
from app.adapters.sql_model_adapter.package.models.package_category import PackageCategory
from app.adapters.sql_model_adapter.package.models.package_price import PackagePrice
from app.adapters.sql_model_adapter.appointment.models.appointment import Appointment
from app.adapters.sql_model_adapter.jotform.models.jotform import JotformCredential, JotformForm, JotformFormAssignment
from app.adapters.sql_model_adapter.jotform.models.jotform_field_mapping import JotformFieldMapping

from app.adapters.session import engine
from app.adapters.sql_model_adapter.package.models.package import Package as PackageSQL
from app.adapters.sql_model_adapter.package.models.package_category import PackageCategory as PackageCategorySQL
from app.adapters.sql_model_adapter.package.models.package_price import PackagePrice as PackagePriceSQL

BUSINESS_ID = 7
CATEGORY_NAME = "Standard Sessions"  # single category, adjust if you split later

PACKAGES = [
    # name, price, photographer_share, business_share, duration, deposit
    ("A - 30 MINUTES", 180, 130, 50, 30, 50),
    ("B - 1 HOUR", 230, 170, 60, 60, 50),
    ("C - 1 HR 30 MINS", 280, 190, 90, 90, 50),
    ("D - 2 HOURS", 350, 250, 100, 120, 50),
    ("E - 2 HRS 30 MINS", 400, 280, 120, 150, 50),
    ("F - 3 HOURS", 450, 310, 140, 180, 50),
    ("SUNSET & NIGHT SESSION - 1", 300, 200, 100, 60, 50),
    ("PARISIAN DREAM 12 HOURS (600 Edited) - €2000", 2000, 2000, 2000, 720, 100),
    ("L'AMOUR FOREVER 8 HOURS (500 Edited) - €1500", 1500, 1500, 1500, 480, 100),
    ("ROMANCE IN PARIS 5 HOURS (350 Edited) - €1000", 1000, 1000, 1000, 300, 100),
    ("TIMELESS MOMENTS 3 HOURS (250 Edited) - €800", 800, 800, 800, 180, 100),
    ("PARIS ELEGANCE EXPRESS 2 HOURS (150 Edited) - €600", 600, 600, 600, 120, 100),
    ("PARIS ESCAPE 1 HOUR (90 Edited) - €400", 400, 400, 400, 60, 100),
    ("DISNEYLAND - 1 HR", 270, 270, 270, 90, 50),
]

# packages whose photographer/business shares are placeholders, not a real split
CUSTOM_QUOTE_PACKAGES = {
    "PARISIAN DREAM 12 HOURS (600 Edited) - €2000",
    "L'AMOUR FOREVER 8 HOURS (500 Edited) - €1500",
    "ROMANCE IN PARIS 5 HOURS (350 Edited) - €1000",
    "TIMELESS MOMENTS 3 HOURS (250 Edited) - €800",
    "PARIS ELEGANCE EXPRESS 2 HOURS (150 Edited) - €600",
    "PARIS ESCAPE 1 HOUR (90 Edited) - €400",
}

def main():
    with Session(engine) as db:
        category = PackageCategorySQL(business_id=BUSINESS_ID, name=CATEGORY_NAME)
        db.add(category)
        db.commit()
        db.refresh(category)

        name_to_package_id = {}

        for name, price, photog_share, biz_share, duration, deposit in PACKAGES:
            pkg = PackageSQL(
                business_id=BUSINESS_ID,
                category_id=category.id,
                name=name,
                description="Custom quote — split not final" if name in CUSTOM_QUOTE_PACKAGES else "",
                is_active=True,
                package_duration=duration,
                jotform_alias=name,  # matches the "Name" column from jotform submissions
            )
            db.add(pkg)
            db.commit()
            db.refresh(pkg)
            name_to_package_id[name] = pkg.id

            price_row = PackagePriceSQL(
                package_id=pkg.id,
                total_price=price,
                deposit_amount=deposit,
                remaining_amount=price - deposit,
                effective_from=datetime(2026, 1, 1),  # backdate before your earliest appointment
            )
            db.add(price_row)
            db.commit()

        print(name_to_package_id)  # paste this dict into the appointment import script

if __name__ == "__main__":
    main()